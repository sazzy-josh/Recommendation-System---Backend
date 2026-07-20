import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='courses.course')),
            ],
            options={
                'db_table': 'course_modules',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='CourseActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('activity_type', models.CharField(
                    choices=[
                        ('quiz', 'Quiz'),
                        ('page', 'Page'),
                        ('assignment', 'Assignment'),
                        ('url', 'URL'),
                    ],
                    max_length=20,
                )),
                ('content', models.TextField(blank=True)),
                ('url', models.URLField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('duration_minutes', models.PositiveIntegerField(blank=True, null=True)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='courses.coursemodule')),
            ],
            options={
                'db_table': 'course_activities',
                'ordering': ['order'],
            },
        ),
    ]
