"""
Definition of models.
"""

from django.db import models

# Create your models here.
class Features(models.Model):
    location = models.CharField(db_column='LOCATION', blank=True, null=False, primary_key=True, max_length=255)  # Field name made lowercase.
    class_field = models.CharField(db_column='CLASS', blank=True, null=True, max_length=255)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    latitude = models.IntegerField(db_column='LATITUDE', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    longitude = models.IntegerField(db_column='LONGITUDE', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    map = models.CharField(db_column='MAP', blank=True, null=True, max_length=255)  # Field name made lowercase.
    elev = models.IntegerField(db_column='ELEV', blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = False
        db_table = 'FEATURES'


class Flowers(models.Model):
    genus = models.CharField(db_column='GENUS', blank=True, null=True, max_length=255)  # Field name made lowercase.
    species = models.CharField(db_column='SPECIES', blank=True, null=True, max_length=255)  # Field name made lowercase.
    comname = models.CharField(db_column='COMNAME', blank=True, null=False, primary_key=True, max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'FLOWERS'


class Members(models.Model):
    name = models.CharField(db_column='NAME', primary_key=True, blank=True, null=False, max_length=255)  # Field name made lowercase.
    membersince = models.DateField(db_column='MEMBERSINCE', blank=True, null=True, max_length=255)  # Field name made lowercase.
    numsightings = models.IntegerField(db_column='NUMSIGHTINGS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MEMBERS'


class Sightings(models.Model):
    id = models.IntegerField(db_column='id', primary_key=True, null=False)
    name = models.CharField(db_column='NAME', blank=True, null=True, max_length=255)  # Field name made lowercase.
    person = models.CharField(db_column='PERSON', blank=True, null=True, max_length=255)  # Field name made lowercase.
    location = models.CharField(db_column='LOCATION', blank=True, null=True, max_length=255)  # Field name made lowercase.
    sighted = models.DateField(db_column='SIGHTED', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SIGHTINGS'