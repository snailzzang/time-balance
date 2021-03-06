from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from timeline.models import *


@login_required
def account(request, user_id):
	owner = get_object_or_404(User, pk=user_id)
	timeline = get_object_or_404(Timeline, owner=owner)

	same_user = request.user.pk == owner.pk
	has_permission = timeline.viewers.filter(id=request.user.id).exists()

	if (not same_user) and (not has_permission):
		return render(request, '403.html')

	study_list = Study.objects.filter(user=owner).order_by('-date')
	categories = Category.objects.filter(user=owner)

	request.user.get_profile_image()

	context = {
		'study_list' : study_list,
		'categories' : categories,
		'owner' : owner,
	}
	return render(request, 'timeline/account.html', context)


@login_required
def add(request):
	json = {
		'result': 'error',
	}

	if not request.POST['viewer_id_to_add']:
		return JsonResponse(json)

	try:
		timeline = Timeline.objects.get(owner=request.user)
	except Timeline.DoesNotExist:
		return JsonResponse(json)

	user = request.user
	viewer_id = int(request.POST['viewer_id_to_add'])

	try:
		viewer = User.objects.get(pk=viewer_id)
		if viewer_id == request.user.id:
			pass
		elif not timeline.viewers.filter(id=viewer_id).exists():
			timeline.viewers.add(viewer)
			json["result"] = "success"
			json["viewer_id"] = viewer_id
	except User.DoesNotExist:
		pass

	return JsonResponse(json)

@login_required
def delete(request):
	json = {
		'result': 'error',
	}

	if not request.POST.getlist('each_id_to_del'):
		return JsonResponse(json)

	viewer_id_list_to_del = request.POST.getlist('each_id_to_del')

	user = request.user
	timeline = Timeline.objects.get(owner=request.user)

	for each_id in viewer_id_list_to_del:
		viewer = User.objects.get(pk=int(each_id))
		timeline.viewers.remove(viewer)
		json["result"] = "success"
		json["viewer_id_list_to_del"] = viewer_id_list_to_del

	return JsonResponse(json)
