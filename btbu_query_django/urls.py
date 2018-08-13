"""btbu_query_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from binding import views as binding_views
from grade_query import views as grade_view
from classTable_query import views as classTable_view
from gpa_query import views as gpa_view
from card_query import views as card_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # 绑定相关
    path('binding', binding_views.index),                           # 绑定查询
    path('binding/do', binding_views.doBinding),                    # 绑定操作
    path('binding/withdraw', binding_views.withdrawBinding),        # 取消绑定

    # 成绩查询相关
    path('grade/', grade_view.grade),

    # 绩点查询相关
    path('gpa/', gpa_view.gpa),

    # 课表查询相关
    path('curriculum/available_data', classTable_view.available_data),  # 获取可查询的数据
    path('curriculum/get', classTable_view.get),             # 获取具体数据
    path('curriculum/current', classTable_view.current),             # 获取当前周数、学期

    # 一卡通查询相关
    path('card/get', card_view.get), # 直接反馈数据
]
