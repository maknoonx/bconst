from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
import json

def home(request):
    context = {
        'company_name': 'باء البناء للمقاولات',
        'company_name_en': 'B Construction Company',
        'services': [
            'الخدمات المعمارية',
            'الخدمات الإنشائية',
            'التصاميم'
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

@require_http_methods(["POST"])
def submit_contact_form(request):
    """معالجة نموذج التواصل وإرسال البريد الإلكتروني"""
    try:
        data = json.loads(request.body)
        phone = data.get('phone', '')
        first_name = data.get('first_name', '')
        email = data.get('email', '')
        
        # التحقق من البيانات
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'البريد الإلكتروني مطلوب'
            }, status=400)
        
        # إعداد محتوى البريد
        subject = f'طلب تواصل جديد من {first_name}'
        message = f"""
        طلب تواصل جديد من موقع باء البناء للمقاولات
        
        الاسم الأول: {first_name}
        البريد الإلكتروني: {email}
        رقم الهاتف: {phone}
        
        تاريخ الإرسال: {data.get('timestamp', '')}
        """
        
        # إرسال البريد
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            ['b.construction.med@gmail.com'],
            fail_silently=False,
        )
        
        return JsonResponse({
            'success': True,
            'message': 'تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'حدث خطأ أثناء الإرسال: {str(e)}'
        }, status=500)

def employee_login(request):
    """صفحة تسجيل الدخول للموظفين - قيد التطوير"""
    return render(request, 'website/employee_login.html')

def architectural_services(request):
    """صفحة الخدمات المعمارية"""
    return render(request, 'website/architectural_services.html')

def structural_services(request):
    """صفحة الخدمات الإنشائية"""
    return render(request, 'website/structural_services.html')

def design_services(request):
    """صفحة خدمات التصاميم"""
    return render(request, 'website/design_services.html')

def about(request):
    """صفحة من نحن"""
    return render(request, 'website/about.html')

def team(request):
    """صفحة فريق العمل"""
    context = {
        'management': [
            {
                'name': 'م. أسامة محبوب',
                'position': 'مدير مشاريع مهندس كهرباء',
                'bio': 'خبرة واسعة في إدارة المشاريع الهندسية الكبرى وتنفيذ الأنظمة الكهربائية المتطورة',
                'experience': '15+ سنة خبرة',
                'image': 'team/manager.svg'
            }
        ],
        'engineers': [
            {'name': 'م. أحمد عطار', 'position': 'مهندس معماري', 'specialty': 'هندسة معمارية', 'image': 'team/engineer1.svg'},
            {'name': 'م. ربيع محمد', 'position': 'مهندس معماري', 'specialty': 'هندسة معمارية', 'image': 'team/engineer2.svg'},
            {'name': 'م. بكر خراط', 'position': 'مهندس معماري', 'specialty': 'هندسة معمارية', 'image': 'team/engineer3.svg'},
            {'name': 'م. طارق بغدادي', 'position': 'مهندس معماري', 'specialty': 'هندسة معمارية', 'image': 'team/engineer4.svg'},
            {'name': 'م. ربيع صالح', 'position': 'مهندس ميكانيك', 'specialty': 'هندسة ميكانيك', 'image': 'team/engineer5.svg'},
            {'name': 'م. عيث بادر', 'position': 'مهندس مدني', 'specialty': 'هندسة مدني', 'image': 'team/engineer6.svg'},
            {'name': 'م. رامي يوسف', 'position': 'مهندس مدني', 'specialty': 'هندسة مدني', 'image': 'team/engineer7.svg'},
            {'name': 'م. منير صباغ', 'position': 'مهندس مدني', 'specialty': 'هندسة مدني', 'image': 'team/engineer8.svg'},
            {'name': 'م. سهيل شحات', 'position': 'مهندس كهرباء', 'specialty': 'هندسة كهرباء', 'image': 'team/engineer9.svg'},
            {'name': 'م. حسن عبدالغني', 'position': 'مهندس كهرباء', 'specialty': 'هندسة كهرباء', 'image': 'team/engineer10.svg'},
            {'name': 'م. عبدالله اليوسف', 'position': 'مهندس كهرباء', 'specialty': 'هندسة كهرباء', 'image': 'team/engineer11.svg'},
            {'name': 'م. محمد إبراهيم', 'position': 'مهندس ميكانيك', 'specialty': 'هندسة ميكانيك', 'image': 'team/engineer12.svg'},
        ],
        'technicians': [
            {'name': 'إدريس خان', 'position': 'فني كهرباء', 'image': 'team/tech1.svg'},
            {'name': 'عرفان خان', 'position': 'فني كهرباء', 'image': 'team/tech2.svg'},
            {'name': 'سيام أبو سيام', 'position': 'فني كهرباء', 'image': 'team/tech3.svg'},
            {'name': 'أصيل حسين', 'position': 'فني كهرباء', 'image': 'team/tech4.svg'},
            {'name': 'سلامة محمد', 'position': 'فني سباكة', 'image': 'team/tech5.svg'},
            {'name': 'وزير إسلام', 'position': 'فني سباكة', 'image': 'team/tech6.svg'},
            {'name': 'عرفان شاكر', 'position': 'فني سباكة', 'image': 'team/tech7.svg'},
            {'name': 'محمد شاكر', 'position': 'فني سباكة', 'image': 'team/tech8.svg'},
            {'name': 'مصباح خان', 'position': 'فني حجان', 'image': 'team/tech9.svg'},
            {'name': 'عبدالوالب محمد', 'position': 'فني بناسة', 'image': 'team/tech10.svg'},
            {'name': 'أحمد عبده', 'position': 'فني بناسة', 'image': 'team/tech11.svg'},
            {'name': 'محمد ادخاي', 'position': 'فني بناسة', 'image': 'team/tech12.svg'},
            {'name': 'ظفر خان', 'position': 'فني بلاط', 'image': 'team/tech13.svg'},
            {'name': 'إلياس حسين', 'position': 'فني حجان', 'image': 'team/tech14.svg'},
            {'name': 'طالب حسين', 'position': 'فني حجان', 'image': 'team/tech15.svg'},
            {'name': 'عمر خان', 'position': 'فني حجان', 'image': 'team/tech16.svg'},
            {'name': 'شهزاد خان', 'position': 'فني بلاط', 'image': 'team/tech17.svg'},
            {'name': 'شاهد اكبر', 'position': 'فني بلاط', 'image': 'team/tech18.svg'},
        ]
    }
    return render(request, 'website/team.html', context)

def privacy_policy(request):
    """صفحة سياسة الخصوصية"""
    return render(request, 'website/privacy_policy.html')

def terms_conditions(request):
    """صفحة الشروط والأحكام"""
    return render(request, 'website/terms_conditions.html')

def project_detail(request, project_id):
    """صفحة تفاصيل المشروع"""
    projects_data = {
        1: {
            'title': 'مشروع النخبة السكني',
            'subtitle': 'مجمع سكني فاخر يجمع بين الرفاهية والراحة في قلب المدينة',
            'status': 'مكتمل',
            'location': 'الرياض، حي النخيل',
            'area': '45,000 م²',
            'units': '120 وحدة',
            'start_date': 'يناير 2022',
            'end_date': 'ديسمبر 2024',
            'type': 'سكني',
            'main_image': 'https://ext.same-assets.com/2977916181/4234824831.png'
        },
        2: {
            'title': 'مشروع الزهراء التجاري',
            'subtitle': 'مجمع تجاري حديث يضم أفضل العلامات التجارية',
            'status': 'قيد التنفيذ',
            'location': 'جدة، حي الزهراء',
            'area': '30,000 م²',
            'units': '85 محل تجاري',
            'start_date': 'مارس 2024',
            'end_date': 'ديسمبر 2025',
            'type': 'تجاري',
            'main_image': 'https://ext.same-assets.com/2977916181/1160599726.png'
        },
        3: {
            'title': 'مشروع فلل الياسمين',
            'subtitle': 'فلل سكنية فاخرة بتصاميم عصرية ومساحات واسعة',
            'status': 'مكتمل',
            'location': 'الدمام، حي الياسمين',
            'area': '50,000 م²',
            'units': '40 فيلا',
            'start_date': 'يونيو 2021',
            'end_date': 'أغسطس 2023',
            'type': 'سكني',
            'main_image': 'https://ext.same-assets.com/2977916181/351238446.png'
        },
        4: {
            'title': 'برج الأندلس الإداري',
            'subtitle': 'برج إداري متكامل بأحدث المواصفات العالمية',
            'status': 'مكتمل',
            'location': 'الرياض، حي الأندلس',
            'area': '25,000 م²',
            'units': '180 مكتب',
            'start_date': 'يناير 2020',
            'end_date': 'يونيو 2023',
            'type': 'إداري',
            'main_image': 'https://ext.same-assets.com/2977916181/2266948137.jpeg'
        },
        5: {
            'title': 'مشروع التميز السكني',
            'subtitle': 'مجمع سكني متميز بموقع استراتيجي ومرافق حديثة',
            'status': 'قيد التنفيذ',
            'location': 'مكة المكرمة، حي العزيزية',
            'area': '35,000 م²',
            'units': '95 وحدة',
            'start_date': 'سبتمبر 2024',
            'end_date': 'مارس 2026',
            'type': 'سكني',
            'main_image': 'https://ext.same-assets.com/2977916181/476409975.jpeg'
        },
        6: {
            'title': 'مشروع جنان السكني',
            'subtitle': 'حياة هادئة وسط الطبيعة في مجمع سكني راقي',
            'status': 'مكتمل',
            'location': 'الطائف، حي الشهداء',
            'area': '40,000 م²',
            'units': '110 وحدة',
            'start_date': 'أبريل 2022',
            'end_date': 'نوفمبر 2024',
            'type': 'سكني',
            'main_image': 'https://ext.same-assets.com/2977916181/1656347559.png'
        }
    }
    
    project = projects_data.get(project_id, projects_data[1])
    
    context = {
        'project': project,
        'project_id': project_id
    }
    
    return render(request, 'website/project_detail.html', context)