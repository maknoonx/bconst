from django.shortcuts import render

def home(request):
    context = {
        'company_name': 'باء البناء للمقاوالت',
        'company_name_en': 'B Construction Company',
        'services': [
            'الخدمات المعمارية',
            'الخدمات الإنشائية', 
            'خدمات التصاميم',
            'خدمات أخرى'
        ],
        'projects': [
            {'name': 'تصميم مسجد', 'image': 'project1.jpg'},
            {'name': 'مسجد رجاء الله', 'image': 'project2.jpg'},
            {'name': 'مسجد القمقجي', 'image': 'project3.jpg'}
        ],
        'contact_info': {
            'address': 'المدينة المنورة، طريق الملك عبدالعزيز',
            'phone': '+966 58 128 7867',
            'email': 'loodxloodx@gmail.com'
        }
    }
    return render(request, 'website/home.html', context)