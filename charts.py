# file charts.py
from . import functions

#Spieler Graph der Skillentwicklung
def Skill_Plot(request,player_id,scale):
    import django
    import datetime
    import numpy
    
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from models import Player, Archiv
    #from matplotlib import pylab
    player=Player.objects.get(id=player_id)
    skill_list = Archiv.objects.filter(player=player).order_by("game_id")
    foo_list=[]
    title = "Spiel"
    if scale =="5": #Yearly-Graph
	for i in range(1,len(skill_list)):
		if skill_list[i].game.time.year == skill_list[i-1].game.time.year:
			continue
		foo_list.append(i-1)
	foo_list.append(len(skill_list)-1)
	#print(foo_list)
	skill_list=[skill_list[i] for i in foo_list]
	title="Jahr"
    elif scale=="4": #Monthly-Graph
	for i in range(1,len(skill_list)):
                if skill_list[i].game.time.month == skill_list[i-1].game.time.month and skill_list[i].game.time.year == skill_list[i-1].game.time.year:
                        continue
                foo_list.append(i-1)
	foo_list.append(len(skill_list)-1)
        skill_list=[skill_list[i] for i in foo_list]
        title="Monat"
    elif scale=="3": #Weekly-Graph
	print("foo - Weekly")
    elif scale=="2": #Daily
	for i in range(1,len(skill_list)):
                if skill_list[i].game.time.day == skill_list[i-1].game.time.day and skill_list[i].game.time.month == skill_list[i-1].game.time.month and skill_list[i].game.time.year == skill_list[i-1].game.time.year:
                        continue
                foo_list.append(i-1)
	foo_list.append(len(skill_list)-1)
        skill_list=[skill_list[i] for i in foo_list]
        title="Tag"
    #Standard-Graph=Gamewise
    number_games = len (skill_list)+1
    fig = Figure()
    ax = fig.add_subplot(111)
    y = [700]
    y_off = [700]
    y_def = [700]
    for i in range(0,len(skill_list)):
        game=skill_list[i]
	skill_overall = functions.compute_skill(game.mu,game.sigma)
	skill_off = functions.compute_skill(game.mu_off,game.sigma_off)
        skill_def = functions.compute_skill(game.mu_def,game.sigma_def)
	y.append(skill_overall)
	y_off.append(skill_off)
	y_def.append(skill_def)
    x = range(0,number_games)
    ax.plot(x, y, '-',label="Allrounder", color="blue")
    ax.plot(x, y_off, '-',label="Offensiv", color="green")
    ax.plot(x, y_def, '-',label="Defensiv", color="red")
    y_values=y
    y_values.extend(y_off)
    y_values.extend(y_def)
    
    ax.get_xaxis().set_ticks(numpy.arange(min(x), max(x)+2, 1.0))
    if scale =="5": #Yearly-Graph
	xaxis_label=["0"]
	for i in range(1,len(skill_list)):
		xaxis_label.append(skill_list[i].game.time.year)
    elif scale=="4": #Monthly-Graph
        print("foo - monthly")
    elif scale=="3": #Weekly-Graph
        print("foo - Weekly")
    elif scale=="2": #Daily
        print("foo - Daily")

    ax.get_yaxis().set_ticks(numpy.arange(min(y_values)-.1*min(y_values), max(y_values)+.1*max(y_values), (max(y_values)-min(y_values))/10))
    for i in range(1,len(x)):
	ax.text(x[i],y[i],y[i], color="blue")
	ax.text(x[i],y_off[i],y_off[i], color="green")
	ax.text(x[i],y_def[i],y_def[i], color="red")
    ax.legend(bbox_to_anchor=(0,-0.12,1,1),loc=8,
           ncol=3, mode="expand", borderaxespad=0.)
    ax.set_title(r'Skillentwicklung ('+title+')')
    canvas = FigureCanvas(fig)
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def skill_all(request, scale, position):
    	import django
    	import datetime
#	import pandas
	import numpy as np

    	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    	from matplotlib.figure import Figure
	import mpld3
	from mpld3 import plugins
    	from matplotlib.dates import DateFormatter,DayLocator, YearLocator, MonthLocator, num2date
	from models import Player
	players = Player.objects.all()
	if scale =="5": #Yearly-Graph
        	title = 'Jahr'
                delta = 365
                pd = functions.compute_graph(
                        players,
                        datetime.date(2015, 04, 01),
                        datetime.date.today()+datetime.timedelta(**{'days': delta}),
                        lambda dt: datetime.datetime(dt.year, 1, 1),
                        delta,
                        position,
                        )
    	elif scale=="4": #Monthly-Graph
        	title = 'Monat'
		delta = 30
		pd = functions.compute_graph(
                        players,
                        datetime.date(2015, 04, 01),
                        datetime.date.today()+datetime.timedelta(**{'days': delta}),
                        lambda dt: datetime.datetime(dt.year, dt.month, 1),
                        delta,
                        position,
                        )
    	elif scale=="3": #Weekly-Graph
        	title = 'Woche'
	elif scale=="2": #Daily
        	title = 'Tag'
		delta = 7
		pd = functions.compute_graph(
                	players,
                	datetime.date(2015, 04, 01),
                	datetime.date.today()+datetime.timedelta(**{'days': delta}),
                	lambda dt: datetime.datetime(dt.year, dt.month, dt.day),
                	delta,
                	position,
		        )
	fig = Figure(figsize=(12,9))
    	ax = fig.add_subplot(111)
	labels = dict()
    	for player, ds in pd.items():
		ax.plot_date(	ds["skill"].keys(),
				ds["skill"].values(),
				'-' ,
				label = player,
				color=ds["color"]) 
		ax.annotate(player.name+" ("+str(ds["skill"].values()[-1])+")", xy=(ds["skill"].keys()[-1],ds["skill"].values()[-1]))
    	ax.set_title(r'Skillentwicklung ('+title+')')
	ax.set_xlim(num2date(ax.get_xlim()[0]),num2date(ax.get_xlim()[1])+datetime.timedelta(**{'days': delta}))
	canvas = FigureCanvas(fig)
    	response=django.http.HttpResponse(content_type='image/png')
    	canvas.print_png(response)
    	return response

