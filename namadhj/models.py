from django.db import models
from django.utils import timezone


class FormCategory(models.Model):
    name = models.CharField(max_length=200, verbose_name='اسم التصنيف')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'تصنيف نموذج'
        verbose_name_plural = 'تصنيفات النماذج'
        ordering = ['name']

    def __str__(self):
        return self.name


class LetterCategory(models.Model):
    name = models.CharField(max_length=200, verbose_name='اسم التصنيف')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'تصنيف خطاب'
        verbose_name_plural = 'تصنيفات الخطابات'
        ordering = ['name']

    def __str__(self):
        return self.name


class Form(models.Model):
    category    = models.ForeignKey(FormCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='التصنيف')
    title       = models.CharField(max_length=300, verbose_name='العنوان الرئيسي')
    content     = models.TextField(verbose_name='النص العام')
    footer_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='اسم الشخص / ملاحظة نهائية')
    date        = models.DateField(default=timezone.now, verbose_name='التاريخ')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'نموذج'
        verbose_name_plural = 'النماذج'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Letter(models.Model):
    category      = models.ForeignKey(LetterCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='التصنيف')
    letter_number = models.CharField(max_length=100, verbose_name='رقم الخطاب')
    title         = models.CharField(max_length=300, verbose_name='عنوان الخطاب')
    recipient     = models.CharField(max_length=300, blank=True, null=True, verbose_name='المرسل إليه')
    subject       = models.CharField(max_length=300, blank=True, null=True, verbose_name='الموضوع')
    content       = models.TextField(verbose_name='نص الخطاب')
    footer_name   = models.CharField(max_length=200, blank=True, null=True, verbose_name='اسم الموقّع / ملاحظة نهائية')
    date          = models.DateField(default=timezone.now, verbose_name='التاريخ')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'خطاب'
        verbose_name_plural = 'الخطابات'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.letter_number} - {self.title}'
