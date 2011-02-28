from django.db import models

class MEPDescriptor(models.Model):
    mep_id = models.CharField(max_length=128, primary_key=True)
    score = models.FloatField()
    country = models.CharField(max_length=2)
    gender = models.CharField(max_length=1)
    birth_year = models.PositiveIntegerField(null=True)
    group = models.CharField(max_length=5)
    
    def __unicode__(self):
        return "<MEPDescriptor id='%s'>" % (self.mep_id)
