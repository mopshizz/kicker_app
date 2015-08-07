# file functions.py
import datetime
from models import Player, Archiv, Game
from django.db.models import Q
from math import factorial

def compute_skill(mu,sigma):
	skill = mu-3*sigma
	return(skill)

def compute_graph(players, start, end, resolution, delta,  position="allround"):
	import collections
	import matplotlib.cm as cm
	import numpy
	q = Archiv.objects.filter(
		Q(game__time__gt = start),
		Q(game__time__lt = end),
		reduce(lambda q1, q2: q1 | q2, map(lambda p: Q(player = p), players))
	    ).order_by('game__time')
 	start=q[0].game.time
	data_plot = dict()
	colors = [c for c in cm.rainbow(numpy.linspace(0,1,len(players)))]
	for skill_record in q:
        	if skill_record.player not in data_plot:
			data_plot[skill_record.player] = dict()
			data_plot[skill_record.player]['color'] = colors.pop()
            		data_plot[skill_record.player]["skill"] = collections.OrderedDict()
			data_plot[skill_record.player]["skill"][start-datetime.timedelta(**{'days': delta})] = 700
		#data_plot[skill_record.player]["skill"][resolution(skill_record.game.time)] = skill_record.player.skill(position=position)
		if position=="offensiv":
			data_plot[skill_record.player]["skill"][resolution(skill_record.game.time)] = compute_skill(skill_record.mu_off,skill_record.sigma_off)
		elif position=="defensiv":
                        data_plot[skill_record.player]["skill"][resolution(skill_record.game.time)] = compute_skill(skill_record.mu_def,skill_record.sigma_def)
		else:
			data_plot[skill_record.player]["skill"][resolution(skill_record.game.time)] = compute_skill(skill_record.mu,skill_record.sigma)
	#colors = cm.rainbow(numpy.linspace(0,1,len(players)))
	#print(data_plot)
	return {p: ds for p, ds in data_plot.items()} 

def calculate_combinations(n, r):
    return factorial(n) // factorial(r) // factorial(n-r)
