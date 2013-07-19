# coding=utf-8
"""
显示数据详情
============

功能
----

该插件可以在列表页中显示相关字段的详细信息, 使用 Ajax 在列表页中显示.

截图
----

.. image:: /images/plugins/details.png

使用
----

使用该插件主要设置 OptionClass 的 ``show_detail_fields``, ``show_all_rel_details`` 两个属性. ``show_detail_fields`` 属性设置哪些字段要显示详细信息, 
``show_all_rel_details`` 属性设置时候自动显示所有关联字段的详细信息, 该属性默认为 ``True``. 示例如下::

    class MyModelAdmin(object):
        
        show_detail_fields = ['group', 'father', ...]

"""
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.db import models

from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, ListAdminView


class DetailsPlugin(BaseAdminPlugin):

    show_detail_fields = []
    show_all_rel_details = True

    def result_item(self, item, obj, field_name, row):
        if (self.show_all_rel_details or (field_name in self.show_detail_fields)):
            rel_obj = None
            if hasattr(item.field, 'rel') and isinstance(item.field.rel, models.ManyToOneRel):
                rel_obj = getattr(obj, field_name)
            elif field_name in self.show_detail_fields:
                rel_obj = obj

            if rel_obj:
                if rel_obj.__class__ in site._registry:
                    try:
                        model_admin = site._registry[rel_obj.__class__]
                        has_view_perm = model_admin(self.admin_view.request).has_view_permission(rel_obj)
                        has_change_perm = model_admin(self.admin_view.request).has_change_permission(rel_obj)
                    except:
                        has_view_perm = self.admin_view.has_model_perm(rel_obj.__class__, 'view')
                        has_change_perm = self.has_model_perm(rel_obj.__class__, 'change')
                else:
                    has_view_perm = self.admin_view.has_model_perm(rel_obj.__class__, 'view')
                    has_change_perm = self.has_model_perm(rel_obj.__class__, 'change')

            if rel_obj and has_view_perm:
                opts = rel_obj._meta
                item_res_uri = reverse(
                    '%s:%s_%s_detail' % (self.admin_site.app_name,
                                         opts.app_label, opts.module_name),
                    args=(getattr(rel_obj, opts.pk.attname),))
                if item_res_uri:
                    if has_change_perm:
                        edit_url = reverse(
                            '%s:%s_%s_change' % (self.admin_site.app_name, opts.app_label, opts.module_name),
                            args=(getattr(rel_obj, opts.pk.attname),))
                    else:
                        edit_url = ''
                    item.btns.append('<a data-res-uri="%s" data-edit-uri="%s" class="details-handler" rel="tooltip" title="%s"><i class="icon-info-sign"></i></a>'
                                     % (item_res_uri, edit_url, _(u'Details of %s') % str(rel_obj)))
        return item

    # Media
    def get_media(self, media):
        if self.show_all_rel_details or self.show_detail_fields:
            media = media + self.vendor('xadmin.plugin.details.js',
                                        'xadmin.modal.css', 'xadmin.form.css')
        return media

site.register_plugin(DetailsPlugin, ListAdminView)
