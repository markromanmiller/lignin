import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from .models import Paper, Question, Value, Column, LigninUser, Subpaper
from collections import defaultdict
import requests
from rules import has_perm

import environ
env = environ.Env()
environ.Env.read_env()


def index(request):
    pks = [i.pk for i in Question.objects.all() if has_perm('ligninapp.view_question', request.user, i)]
    visible_questions = Question.objects.filter(id__in=pks)

    return render(request, template_name="ligninapp/index.html", context={
        "visible_questions": visible_questions
    })

def get_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    return render(request, template_name="ligninapp/question.html", context={
        "question": question,
        "question_id": question_id
    })


def add_paper(request, question_id, paper_id):
    # check if the paper exists.
    paper_match_set = Paper.objects.filter(ssPaperID=paper_id)
    if paper_match_set:
        paper_match = paper_match_set[0]
    else:
        # make API call to Semantic Scholar.
        paper_details = requests.get(
            f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
            f"?fields=title,year,authors,citations.paperId,references.paperId"
        ).json()

        new_paper = Paper.objects.create(
            ssPaperID=paper_details['paperId'],
            title=paper_details['title'],
            year=int(paper_details['year']),
            faln=paper_details['authors'][0]['name'] + (" et al." if len(paper_details['authors']) > 1 else ""),
            references=" ".join([x["paperId"] for x in paper_details['references'] if x["paperId"]]),
            citations=" ".join([x["paperId"] for x in paper_details['citations'] if x["paperId"]]),
            url=f"https://www.semanticscholar.org/paper/{paper_details['paperId']}"
        )
        new_paper.save()
        paper_match = new_paper

    subpaper = paper_match.default_subpaper
    if subpaper is None:
        subpaper = Subpaper.objects.create(paper=paper_match, description="")
        subpaper.save()
        paper_match.default_subpaper = subpaper
        paper_match.save()

    Question.objects.get(id=question_id).papers.add(subpaper)

    return HttpResponse(status=201)


def get_papers(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    # get columns for that question.
    columns = question.columns.all()

    # loop through the serialized files and pull relevant info
    result = []
    for subpaper in question.papers.all(): # these are objects, one by one.
        paper = subpaper.paper
        # extract the basics (year, faln, etc)
        paper_json = json.loads(serializers.serialize(
            'json',
            Paper.objects.filter(pk=subpaper.paper.pk),
            fields=['ssPaperID', 'title', 'year', 'faln', 'url']))

        paper_info = paper_json[0]["fields"]  # there's guaranteed to be one.
        paper_info["description"] = subpaper.description
        for column in columns:
            descriptions = Value.objects.filter(column=column, paper=subpaper)
            paper_info[column.name] = descriptions[0].value if descriptions else ""

        result.append(paper_info)
        #

    column_mds = {}
    for column in columns:
        column_mds[column.name] = column.pk

    return JsonResponse({
        "data": result,
        "column_nums": column_mds
    })


def edit_annotation(request, paper_id, column_pk):
    # if it already exists, edit it.
    value_text = request.POST["value_text"]
    note_text = request.POST["note_text"]
    paper = get_object_or_404(Paper, ssPaperID=paper_id)
    column = get_object_or_404(Column, pk=column_pk)
    lignin_user = get_object_or_404(LigninUser, owner=request.user)

    value, was_created = Value.objects.get_or_create(paper=paper, column=column, creator=lignin_user)
    value.value = value_text
    # value.notes = note_text
    value.save()
    return HttpResponse(200)


def reject_paper(request, question_id, paper_id):
    question = get_object_or_404(Question, id=question_id)

    # if it's already there, ignore the request.
    if paper_id in question.rejected_papers:
        return HttpResponse(204)

    # Otherwise, add the paper (with perhaps a space)
    if question.rejected_papers:
        question.rejected_papers += " " + paper_id
    else:
        question.rejected_papers = paper_id
    question.save()
    return HttpResponse(201)


def get_snowball(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    included_papers = question.papers.all()
    rejected_paper_ids = question.rejected_papers.split(" ") if question.rejected_papers else []
    ignored_paper_ids = [x.ssPaperID for x in included_papers] + rejected_paper_ids
    id_strings = [x.references.split(" ") + x.citations.split(" ") for x in included_papers]
    snowball_set_size = len(id_strings)

    d = defaultdict(int)
    for paper_links in id_strings:
        for paper_id in paper_links:
            d[paper_id] += 1

    most_refs = sorted(d.items(), key=lambda item: item[1], reverse=True)
    most_refs_filtered = [x for x in most_refs if x[0] not in ignored_paper_ids]
    #print(most_refs)
    #print(most_refs_filtered)

    r = requests.post(
        "https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,year,authors,url",
        json={"ids": [x[0] for x in most_refs_filtered[:10]]}
    )

    response = r.json()
    for paper in response:
        paper["occurrence_number"] = d[paper['paperId']]
        paper["occurrence"] = f"{d[paper['paperId']]}/{snowball_set_size}"

    return JsonResponse({"data": sorted(response, key=lambda x: x["occurrence_number"], reverse=True)})

