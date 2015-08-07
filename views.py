from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .models import Game,Player, Archiv
from django.core.urlresolvers import reverse
from django.utils import timezone
from math import floor, ceil, factorial
import random
from .functions import compute_skill,calculate_combinations
from django.db.models import Q

#trueskill package einbinden
from trueskill import Rating,rate,setup,quality

# Create your views here.


#Im index wird die Liste mit allen Spielern angezeigt
def index(request):
	players=Player.objects.all().order_by('name')
	players_list=[[p.name,compute_skill(p.mu,p.sigma),p.id,compute_skill(p.mu_off,p.sigma_off),compute_skill(p.mu_def,p.sigma_def),p.available] for p in players]
	context={'players_list': players_list}
	return render(request, 'kicker_app/index.html', context)

#Im actual_games werden die Spiele ohne Ergebnis angezeigt
def open_games(request):
	games_list=Game.objects.filter(goals_1=0,goals_2=0).order_by('-time')
	#quality_list=[quality([[game.off_player1,game.def_player1],[game.off_player2,game.def_player2]]) for game in games_list]
	context={'games_list': games_list}
        return render(request, 'kicker_app/open_games.html', context)

#Im games werden die letzten Spiele angezeigt
def games(request):
        games_list=Game.objects.order_by('-time')
        context={'games_list': games_list}
        return render(request, 'kicker_app/games.html', context)

#Graph mit Skill-Entwicklung
def skill(request, scale=2, position="allrounder"):
        games_list=Archiv.objects.order_by('time')
	if position not in ["allrounder", "offensiv", "defensiv"]:
		position = "allrounder"
        context={'scale': scale,
		 'position': position}
        return render(request, 'kicker_app/skill.html', context)


def player_profile(request,player_id, scale=1):
	player = Player.objects.get(id=player_id)
	skill = compute_skill(player.mu,player.sigma)
	def_skill = compute_skill(player.mu_def,player.sigma_def)
	off_skill = compute_skill(player.mu_off,player.sigma_off)
	krabbel_list = Game.objects.filter(
				(
					(Q(off_player1 = player)|Q(def_player1=player))
					&(Q(goals_1=0)&Q(goals_2__gt=0))
				)|
				(
					(Q(off_player2 = player)|Q(def_player2=player))
					&(Q(goals_2=0)&Q(goals_1__gt=0))
				))
	#print("krabbeln:",krabbel_list)
	context={'name': player.name,
		 'player_id':player.id,
		 'skill':skill,
                 'def_skill':def_skill,
                 'off_skill':off_skill,
		 'scale': scale,
		 'krabbel_counter': len(krabbel_list)}
	return render(request, 'kicker_app/profile.html', context)
	


def new_player(request):
	p = Player(name=request.POST['name'])
	p.save()
	return HttpResponseRedirect(reverse('kicker_app:index'))

def switch_availability(request,player_id):
	player=Player.objects.get(id=player_id)
	if player.available:
		player.available=False
	else:
		player.available=True
	player.save()
	return HttpResponseRedirect(reverse('kicker_app:index'))

def save_result(request):
	#Neues Ergebnis eintragen
	#Muss noch Fehlerabfrage einbauen (nur positive Zahlen und kein Draw erlaubt)
	g = Game.objects.get(id=request.POST['game'])
	g.goals_1 = request.POST['goals_1']
	g.goals_2 = request.POST['goals_2']
	g.save()
	if g.goals_1 > g.goals_2:
		foo=1
	else:
		foo=0
	result=[1-foo,foo]
	#Globalen TrueSkill berechnen
	setup(beta=666, draw_probability=0)
	off1 = Rating(mu=g.off_player1.mu,sigma=g.off_player1.sigma)
	def1 = Rating(mu=g.def_player1.mu,sigma=g.def_player1.sigma)
	off2 = Rating(mu=g.off_player2.mu,sigma=g.off_player2.sigma)
	def2 = Rating(mu=g.def_player2.mu,sigma=g.def_player2.sigma)
	team1 = [off1,def1]
	team2 = [off2,def2]
	(new_off1,new_def1),(new_off2,new_def2)=rate([team1,team2],result)
	g.off_player1.mu = new_off1.mu
	g.off_player1.sigma = new_off1.sigma
	g.off_player1.save()

        g.off_player2.mu = new_off2.mu
        g.off_player2.sigma = new_off2.sigma
        g.off_player2.save()

        g.def_player1.mu = new_def1.mu
        g.def_player1.sigma = new_def1.sigma
        g.def_player1.save()

        g.def_player2.mu = new_def2.mu
        g.def_player2.sigma = new_def2.sigma
        g.def_player2.save()
	#Positionsskill berechnen
        off1 = Rating(mu=g.off_player1.mu_off,sigma=g.off_player1.sigma_off)
        def1 = Rating(mu=g.def_player1.mu_def,sigma=g.def_player1.sigma_def)
        off2 = Rating(mu=g.off_player2.mu_off,sigma=g.off_player2.sigma_off)
        def2 = Rating(mu=g.def_player2.mu_def,sigma=g.def_player2.sigma_def)
        team1 = [off1,def1]
        team2 = [off2,def2]
        (new_off1,new_def1),(new_off2,new_def2)=rate([team1,team2],result)
        g.off_player1.mu_off = new_off1.mu
        g.off_player1.sigma_off = new_off1.sigma
        g.off_player1.save()

        g.off_player2.mu_off = new_off2.mu
        g.off_player2.sigma_off = new_off2.sigma
        g.off_player2.save()

        g.def_player1.mu_def = new_def1.mu
        g.def_player1.sigma_def = new_def1.sigma
        g.def_player1.save()

        g.def_player2.mu_def = new_def2.mu
        g.def_player2.sigma_def = new_def2.sigma
        g.def_player2.save()
	archiv=Archiv(game=g,player=g.off_player1,mu=g.off_player1.mu,sigma=g.off_player1.sigma,mu_off=g.off_player1.mu_off,sigma_off=g.off_player1.sigma_off,mu_def=g.off_player1.mu_def,sigma_def=g.off_player1.sigma_def)
	archiv.save()
	archiv=Archiv(game=g,player=g.def_player1,mu=g.def_player1.mu,sigma=g.def_player1.sigma,mu_off=g.def_player1.mu_off,sigma_off=g.def_player1.sigma_off,mu_def=g.def_player1.mu_def,sigma_def=g.def_player1.sigma_def)
        archiv.save()
	archiv=Archiv(game=g,player=g.off_player2,mu=g.off_player2.mu,sigma=g.off_player2.sigma,mu_off=g.off_player2.mu_off,sigma_off=g.off_player2.sigma_off,mu_def=g.off_player2.mu_def,sigma_def=g.off_player2.sigma_def)
        archiv.save()
	archiv=Archiv(game=g,player=g.def_player2,mu=g.def_player2.mu,sigma=g.def_player2.sigma,mu_off=g.def_player2.mu_off,sigma_off=g.def_player2.sigma_off,mu_def=g.def_player2.mu_def,sigma_def=g.def_player2.sigma_def)
        archiv.save()
	
	return HttpResponseRedirect(reverse('kicker_app:open_games'))

def save_match(match):
	game=Game(off_player1=match[0][0], def_player1=match[0][1], off_player2=match[1][0], def_player2=match[1][1],time=timezone.now())
	game.save()
	match[0][0].number_games+=1
	match[0][0].save()
        match[1][0].number_games+=1
        match[1][0].save()
        match[0][1].number_games+=1
        match[0][1].save()
        match[1][1].number_games+=1
        match[1][1].save()

	return True

def calculate_combinations(n, r):
    return factorial(n) // factorial(r) // factorial(n-r)

def deja_vu(match,length):
	date = timezone.now()
	timedelta = timezone.timedelta(days=1)
	games_list=Game.objects.filter(time__gt = date - timedelta).order_by('-time')[:floor(calculate_combinations(length,2)/2)-1]
	recent_teams=set()
	for game in games_list:
		recent_teams.add(frozenset([game.off_player1,game.def_player1]))
		recent_teams.add(frozenset([game.off_player2,game.def_player2]))
	#print(floor(calculate_combinations(length,2)/2)-1,recent_teams)
	if frozenset(match[0]) in recent_teams or frozenset(match[1]) in recent_teams:
		#print(calculate_combinations(length,2),match)
		return True
	else:
		return False
	

def create_match(available_players):
	if len(available_players)>=4:
                games_list=[]
                #berechne alle moeglichen paarungen
                for player_1 in available_players:
                        for player_2 in available_players:
                                if player_2==player_1:
                                        continue
                                for player_3 in available_players:
                                        if player_3==player_1 or player_3==player_2:
                                                continue
                                        for player_4 in available_players:
                                                if player_4==player_1 or player_4==player_2 or player_4==player_3:
                                                        continue
                                                games_list.append([[player_1,player_2],[player_3,player_4]])
                best_game=games_list[0]
                for game in games_list:
                        if quality(game)>quality(best_game):
                                best_game=game
                #waehle alle spiele, welche in der qualitaet nur um 0% vom besten spiel abweichen
                best_games=[]
                for game in games_list:
                        if quality(game)>(quality(best_game)-1*quality(best_game)):
                                best_games.append(game)
		#print(len(games_list),len(best_games))
                #waehle aus dieser liste die spiele aus, wo in summe am seltensten gespielt wurde
                best_number=(best_game[0][0].number_games+best_game[0][1].number_games+best_game[1][1].number_games+best_game[1][0].number_games)
                for game in best_games:
                        game_number=(game[0][0].number_games+game[0][1].number_games+game[1][1].number_games+game[1][0].number_games)
                        if game_number<best_number:
                                best_game=game
                games_list=[best_game]
                for game in best_games:
                        game_number=(game[0][0].number_games+game[0][1].number_games+game[1][1].number_games+game[1][0].number_games)
                        if (game_number-game_number)<(best_number):
                                games_list.append(game)
		return games_list

def new_match(request):
	#manuelles match erstellen
	return HttpResponseRedirect(reverse('kicker_app:open_games'))


def new_skill_match(request):
	#match mit trueskill erzeugen
	#waehle spieler aus der datenbank, die anwesend sind und mindestens x(anzahl spieler) spiele nicht gespielt haben
	player_list=Player.objects.filter(available=True)
	#print("Spieler anwesend:",player_list)
	if len(player_list)<4:
			print("Nicht genug Spieler anwesend")
		        return HttpResponseRedirect(reverse('kicker_app:open_games'))
	elif len(player_list) == 4:
		games_list=create_match(player_list)
		available_players = player_list
	else:
		games_all=Game.objects.order_by('-id')
		available_players = set()
		i = -1
		while len(available_players)<5:
			max_games=(len(player_list)//4)-i
			games_list=games_all[:max_games]
			recent_players=[]
			for game in games_list:
				recent_players.extend([game.off_player1,game.off_player2,game.def_player1,game.def_player2])
			#print("Spieler die gespielt haben:", recent_players)
			i+=1
			available_players=set(player_list)-set(recent_players)
			#print ("Pool:",available_players)
		games_list=create_match(available_players)
	game_found=False
	date = timezone.now()
        timedelta = timezone.timedelta(days=1)
        games_played=Game.objects.filter(time__gt = date - timedelta).order_by('-time')[:(calculate_combinations(len(player_list),2)/2)-1]
        recent_teams=set()
        for game in games_played:
                recent_teams.add(frozenset([game.off_player1,game.def_player1]))
                recent_teams.add(frozenset([game.off_player2,game.def_player2]))
	i = 0
	while not game_found:
		match=random.choice(games_list)
		#print(match)
		#teste maximal #games_list elemente aus der liste. anschliessend nimm das letzte -> Verhindert haengenbleiben in der schleife.
		if i == len(games_list):
			print("notausstieg")
			game_found = True
		i +=1
		if not (frozenset(match[0]) in recent_teams) and not (frozenset(match[1]) in recent_teams):
                	print(match)
                	game_found = True
        save_match(match)
	return HttpResponseRedirect(reverse('kicker_app:open_games'))

def delete_open_game(request):
	Game.objects.get(id = request.POST["game"]).delete()
	return HttpResponseRedirect(reverse('kicker_app:open_games'))
