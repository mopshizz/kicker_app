from django.db import models

# Create your models here.

class Player(models.Model):
        name=           models.CharField(max_length=200)
        mu=             models.IntegerField(default=2500)
        sigma=          models.IntegerField(default=600)
        mu_off=             models.IntegerField(default=2500)
        sigma_off=          models.IntegerField(default=600)
        mu_def=             models.IntegerField(default=2500)
        sigma_def=          models.IntegerField(default=600)
	available=	models.BooleanField(default=True)
	number_games= models.IntegerField(default=0)
	def __str__(self):
		return self.name
        def skill(self,position='allround'):
                if position == 'allround':
                        return self.mu-3*self.sigma
                if position == 'defensiv':
                        return self.mu_def-3*self.sigma_def
                if position == 'offensiv':
                        return self.mu_off-3*self.sigma_off

class Game(models.Model):
	time=		models.DateTimeField('date published')
	off_player1=		models.ForeignKey(Player, related_name='off_1', null=True)
	def_player1=            models.ForeignKey(Player, related_name='def_1', null=True)
	off_player2=		models.ForeignKey(Player, related_name='off_2', null=True)
        def_player2=            models.ForeignKey(Player, related_name='def_2', null=True)
	goals_1=	models.IntegerField(default=0)
	goals_2=        models.IntegerField(default=0)
	def __str__(self):
		return self.off_player1.name+'/'+self.def_player1.name+' vs '+self.off_player2.name+'/'+self.def_player2.name

class Archiv(models.Model):
	game=		models.ForeignKey(Game)
	player= 	models.ForeignKey(Player)
	mu=             models.IntegerField(default=2500)
        sigma=          models.IntegerField(default=600)
        mu_off=         models.IntegerField(default=2500)
        sigma_off=      models.IntegerField(default=600)
        mu_def=         models.IntegerField(default=2500)
        sigma_def=      models.IntegerField(default=600)
        def __str__(self):
                return self.player.name +  ' - ' + str(self.mu)
