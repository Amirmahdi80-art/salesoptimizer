from django.contrib import admin

from .models import (
    CategoryContrAvgs,
    Color,
    CumulativeProductLookup,
    InvoiceItems,
    InvoiceItemsParent,
    ProductCategories,
    ProductsLookup,
    StoreMapping,
    TwelveMonthAnalysis,
    TwelveMonthAnalysisStore,
    AnalysisGradeOne,
    Action,
    ProductVoucher
)


@admin.register(CategoryContrAvgs)
class CategoryContrAvgsAdmin(admin.ModelAdmin):
    list_display = ("category_code", "category_name", "avg_discount_percentage")
    search_fields = ("category_code", "category_name")
    ordering = ("category_code",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "color")
    search_fields = ("code", "color")
    ordering = ("color",)


@admin.register(CumulativeProductLookup)
class CumulativeProductLookupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "parent_code",
        "name",
        "category_code",
        "sales_office_id",
        "expr2",
        "cumulative_qty",
        "cumulative_price",
    )
    list_filter = ("category_code", "sales_office_id")
    search_fields = ("parent_code", "name", "expr1")
    ordering = ("-id",)
    date_hierarchy = "expr2"
    list_per_page = 50


@admin.register(InvoiceItems)
class InvoiceItemsAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_item_id",
        "invoice_id",
        "code",
        "name",
        "sales_office_id",
        "expr2",
        "major_unit_quantity",
        "net_price",
    )
    list_filter = ("sales_office_id",)
    search_fields = ("code", "name", "number", "full_name", "mobile")
    ordering = ("-invoice_item_id",)
    date_hierarchy = "expr2"
    list_per_page = 50


@admin.register(InvoiceItemsParent)
class InvoiceItemsParentAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_item_id",
        "invoice_id",
        "parent_code",
        "name",
        "sales_office_id",
        "expr2",
        "major_unit_quantity",
        "net_price",
    )
    list_filter = ("sales_office_id",)
    search_fields = ("parent_code", "name", "number", "full_name", "mobile")
    ordering = ("-invoice_item_id",)
    date_hierarchy = "expr2"
    list_per_page = 50


@admin.register(ProductCategories)
class ProductCategoriesAdmin(admin.ModelAdmin):
    list_display = ("id", "category_code", "category_name")
    search_fields = ("category_code", "category_name")
    ordering = ("category_code",)


@admin.register(ProductsLookup)
class ProductsLookupAdmin(admin.ModelAdmin):
    list_display = (
        "product_code",
        "category_code",
        "total_inventory",
        "first_show_date",
        "days_since_entry",
        "days_since_show",
    )
    list_filter = ("category_code",)
    search_fields = ("product_code",)
    ordering = ("product_code",)
    date_hierarchy = "first_show_date"
    list_per_page = 50


@admin.register(StoreMapping)
class StoreMappingAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "voucher_store_id", "invoice_store_id")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(TwelveMonthAnalysis)
class TwelveMonthAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        "product_code",
        "category_code",
        "age_in_months",
        "total_sold_12_months",
        "discount_percentage",
        "first_show_date",
    )
    list_filter = ("category_code",)
    search_fields = ("product_code",)
    ordering = ("-total_sold_12_months",)
    date_hierarchy = "first_show_date"
    list_per_page = 50


@admin.register(TwelveMonthAnalysisStore)
class TwelveMonthAnalysisStoreAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_code",
        "sales_office_id",
        "name",
        "category_code",
        "age_in_months",
        "total_sold_12_months",
    )
    list_filter = ("category_code", "sales_office_id")
    search_fields = ("product_code", "name")
    ordering = ("-id",)
    list_per_page = 50


@admin.register(AnalysisGradeOne)
class AnalysisGradeOneAdmin(admin.ModelAdmin):
    list_display = (
        "product_code",
        "category_code",
        "status_tag",
        "action",
        "age_in_months",
        "total_sold_12_months",
        "remaining_months",
        "discount_quality",
        "completed",
    )
    list_filter = (
        "category_code",
        "status_tag",
        "action",
        "discount_quality",
        "completed",
    )
    search_fields = ("product_code",)
    ordering = ("product_code",)
    list_per_page = 50


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_code",
        "action_number",
        "action_type",
        "action_target",
        "action_start_date",
        "action_end_date",
        "action_verdict",
        "created_by",
        "action_created_date",
    )
    list_filter = (
        "action_type",
        "action_verdict",
        "action_created_date",
        "action_start_date",
        "action_end_date",
    )
    search_fields = (
        "product_code",
        "action_type",
        "action_target",
        "created_by",
    )
    date_hierarchy = "action_created_date"
    ordering = ("-action_created_date", "-action_number")
    list_per_page = 25

    # Read-only fields (auto-generated or sensitive)
    readonly_fields = ("id", "action_created_date")

    # Group fields nicely on the detail page
    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "id",
                    "product_code",
                    "action_number",
                    "action_type",
                    "action_target",
                )
            },
        ),
        (
            "زمان‌بندی",
            {"fields": ("action_start_date", "action_end_date", "action_created_date")},
        ),
        (
            "نتایج",
            {"fields": ("action_lift", "action_margin_impact", "action_verdict")},
        ),
        ("سایر", {"fields": ("created_by", "notes")}),
    )


@admin.register(ProductVoucher)
class ProductVoucherAdmin(admin.ModelAdmin):
    list_display  = (
        "id",
        "direction",
        "voucher_no",
        "voucher_date",
        "part_code",
        "part_name",
        "source_store",
        "dest_store",
        "qty",
        "spec_ref",
    )
    list_filter   = ("direction", "spec_ref", "source_store", "dest_store")
    search_fields = ("part_code", "part_name", "voucher_no", "voucher_caption")
    ordering      = ("-voucher_date", "-id")
    readonly_fields = ("created_at",)
    date_hierarchy = "voucher_date"


from django.contrib import admin
from django.db import models as db_models
from django import forms
from django.utils.html import mark_safe

from .models import Sqlchunk


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
GUIDE_CSS = """
<style>
.sqlchunk-guide { direction: rtl; text-align: right;
    font-family: Vazirmatn, "Segoe UI", Tahoma, sans-serif;
    line-height: 1.9; color: #1f2933; }
.sqlchunk-guide h1 { font-size: 20px; margin: 0 0 6px; color: #0f172a; }
.sqlchunk-guide .guide-sub { margin: 0 0 14px; color: #52606d; font-size: 13.5px; }

.sqlchunk-guide .guide-warning {
    background: linear-gradient(135deg,#fff5f5 0%,#ffe3e3 100%);
    border: 1px solid #ff6b6b; border-right: 6px solid #e03131;
    border-radius: 12px; padding: 16px 20px; margin: 14px 0;
    box-shadow: 0 2px 6px rgba(224,49,49,.08);
}
.sqlchunk-guide .guide-warning h2 { margin: 0 0 10px; font-size: 16px; color: #c92a2a; }
.sqlchunk-guide .guide-warning p  { margin: 6px 0; font-size: 13.5px; }
.sqlchunk-guide .guide-note {
    background: rgba(255,255,255,.6); border-radius: 8px;
    padding: 8px 12px; margin-top: 8px !important; font-size: 13px !important;
}

.sqlchunk-guide .field-card {
    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 12px 16px; margin-bottom: 10px;
}
.sqlchunk-guide .field-head {
    display: flex; align-items: baseline; gap: 10px;
    margin-bottom: 4px; flex-wrap: wrap;
}
.sqlchunk-guide .field-name code {
    background: #1e293b; color: #7dd3fc; padding: 2px 10px;
    border-radius: 6px; font-size: 12.5px; direction: ltr; display: inline-block;
}
.sqlchunk-guide .field-title { font-weight: 600; color: #334155; font-size: 14.5px; }
.sqlchunk-guide .field-card p { margin: 4px 0; font-size: 13.5px; color: #475569; }
.sqlchunk-guide .field-card ul { margin: 4px 20px 4px 0; padding: 0; font-size: 13px; color: #475569; }
.sqlchunk-guide .field-card li { margin: 2px 0; }

.sqlchunk-guide code {
    background: #eef2ff; color: #4338ca; padding: 1px 6px;
    border-radius: 4px; font-family: "Fira Code","Consolas",monospace;
    font-size: 12.5px; direction: ltr; display: inline-block;
}
.sqlchunk-guide .code-wrap { text-align: center; margin: 10px 0; }
.sqlchunk-guide .code-wrap code {
    font-size: 15px; padding: 6px 16px;
    background: #1e293b; color: #fbbf24; border-radius: 8px; direction: rtl;
}
.sqlchunk-guide .code-block {
    background: #0f172a; color: #e2e8f0; padding: 16px 20px;
    border-radius: 10px; overflow-x: auto; font-size: 13px; line-height: 1.6;
    border: 1px solid #1e293b; direction: ltr; text-align: left;
}
.sqlchunk-guide .code-block code {
    background: transparent; color: inherit; padding: 0; display: block;
    white-space: pre; direction: ltr; font-size: inherit;
}
.sqlchunk-guide .guide-reminder {
    background: linear-gradient(135deg,#ecfdf5 0%,#d1fae5 100%);
    border: 1px solid #10b981; border-right: 6px solid #059669;
    border-radius: 10px; padding: 12px 18px; margin-top: 16px;
    font-size: 13.5px; color: #065f46;
}
</style>
"""


# ---------------------------------------------------------------------------
# Guide HTML (RTL Persian, code elements LTR)
# ---------------------------------------------------------------------------
GUIDE_HTML = GUIDE_CSS + """
<div class="sqlchunk-guide" dir="rtl" lang="fa">
  <h1>راهنمای پیکربندی موتور SQL</h1>
  <p class="guide-sub">
    این صفحه پیکربندی اسکریپت‌های SQL موتور را نمایش می‌دهد.
    لطفاً پیش از هرگونه ویرایش، بخش <strong>هشدارهای حیاتی</strong> را با دقت مطالعه کنید.
  </p>

  <!-- ==================== WARNING ==================== -->
  <div class="guide-warning">
    <h2>⚠️ هشدارهای حیاتی — تغییر نام مقادیر ممنوع است</h2>
    <p>
      در ستون‌های <code>vt</code>، <code>discount_quality</code>، <code>tag</code> و <code>action</code>
      مقادیر ثابتی وجود دارند که <strong>نباید هیچ‌گونه تغییری در آن‌ها ایجاد شود</strong>.
      نام مقادیر باید دقیقاً همان‌طور که هستند باقی بمانند؛
      <strong>زیرخط ( <code>_</code> ) و فاصله‌ها دارای معنا و اهمیت هستند</strong> و
      کوچک‌ترین اشتباه در آن‌ها می‌تواند کل رابط کاربری (UI) را مختل کند.
    </p>
    <p>برای مثال، مقادیر زیر باید دقیقاً به همین شکل باقی بمانند:</p>
    <div class="code-wrap"><code>کامل_شده</code></div>
    <div class="code-wrap"><code>داده_ناکافی</code></div>
    <div class="code-wrap"><code>موجودی_مرده_کامل</code></div>
    <p>
      نه زیرخط را حذف کنید، نه فاصله اضافه یا کم کنید، و نه حروف را تغییر دهید.
    </p>
    <p class="guide-note">
      🔁 <strong>بازگشت به مقادیر پیش‌فرض:</strong>
      در هر لحظه می‌توانید به اسکریپت‌های پیش‌فرض بازگردید.
      کافی است رکورد اول را حذف کرده و یک رکورد جدید اضافه کنید.
    </p>
    <p class="guide-note">
      📌 <strong>ساختار تک‌رکوردی (Singleton):</strong>
      این جدول به‌صورت Singleton طراحی شده است؛ یعنی موتور تنها
      <strong>اولین رکورد</strong> را در نظر می‌گیرد و سایر رکوردها نادیده گرفته می‌شوند.
    </p>
  </div>

  <!-- ==================== FIELD DESCRIPTIONS ==================== -->
  <div class="field-card">
    <div class="field-head">
      <span class="field-name"><code>vt</code></span>
      <span class="field-title">شکاف سرعت (Velocity Gap / VT)</span>
    </div>
    <p>
      این ستون اسکریپت SQL شاخص <strong>شکاف سرعت</strong> را نگه می‌دارد.
      در کوئری مرجع، این بخش دقیقاً جایگزین بلوک <code>@@vt@@</code> در CTE به نام
      <code>metrics</code> می‌شود و باید یک عبارت معتبر SQL با نام مستعار <code>vt</code>
      تولید کند که در خروجی نهایی ظاهر شود.
    </p>
    <p>
      داده‌های پایه در همان CTE موجود است:
      <code>current_velocity</code> (سرعت فروش ماه جاری)،
      <code>prior_velocity</code> (سرعت فروش ماه قبل)،
      <code>velocity_gap</code> (نسبت سرعت فعلی به سرعت مورد نیاز آینده)،
      <code>age_in_months</code>، <code>rstr</code>، <code>cdr</code>، <code>rvr</code>،
      <code>discount_percentage</code> و <code>avg_discount_percentage</code>.
    </p>
    <p>
      مقادیر مجاز در تعریف پیش‌فرض:
    </p>
    <ul>
      <li><code>داده_ناکافی</code> — وقتی <code>age_in_months &lt; 2</code> باشد.</li>
      <li><code>شتاب‌گیرنده</code> — وقتی <code>current_velocity &gt; prior_velocity * 1.10</code>.</li>
      <li><code>نزولی</code> — وقتی <code>current_velocity &lt; prior_velocity * 0.90</code>.</li>
      <li><code>ثابت</code> — در سایر حالات.</li>
    </ul>
    <p>
      استفاده از نام‌های نادرست یا ارجاع به ستون‌های ناموجود باعث خطای اجرای کوئری و شکست کل
      ساخت جدول <code>analysis_grade_one</code> می‌شود.
    </p>
  </div>

  <div class="field-card">
    <div class="field-head">
      <span class="field-name"><code>discount_quality</code></span>
      <span class="field-title">کیفیت تخفیف (Discount Quality)</span>
    </div>
    <p>
      این ستون اسکریپت SQL مربوط به ارزیابی <strong>کیفیت تخفیف</strong> را نگه می‌دارد.
      در کوئری مرجع، این بخش جایگزین بلوک <code>@@discount_quality@@</code> در CTE به نام
      <code>metrics</code> می‌شود و باید یک عبارت معتبر SQL با نام مستعار
      <code>discount_quality</code> تولید کند.
    </p>
    <p>
      داده‌های پایه در همان CTE موجود است:
      <code>discount_percentage</code> (درصد تخفیف محصول) و
      <code>avg_discount_percentage</code> (میانگین درصد تخفیف دستهٔ محصول)،
      و همچنین <code>dd = discount_percentage - avg_discount_percentage</code>
      که اختلاف تخفیف محصول با میانگین دسته را نشان می‌دهد.
    </p>
    <p>
      مقادیر مجاز در تعریف پیش‌فرض:
    </p>
    <ul>
      <li><code>طبیعی</code> — وقتی <code>dd &lt;= 0</code> باشد.</li>
      <li><code>حمایت‌شده</code> — وقتی <code>0 &lt; dd &lt;= 10</code> باشد.</li>
      <li><code>وابسته</code> — وقتی <code>10 &lt; dd &lt;= 25</code> باشد.</li>
      <li><code>در_فشار</code> — وقتی <code>dd &gt; 25</code> باشد.</li>
    </ul>
    <p>
      این مقادیر در CTE <code>tagged</code> برای محاسبهٔ <code>status_tag</code> و
      <code>action</code> استفاده می‌شوند؛ تغییر در نام یا حذف یکی از آن‌ها
      باعث می‌شود شرط‌های <code>CASE WHEN</code> برقرار نشوند و برچسب نهایی
      و اقدام پیشنهادی نادرست شود.
    </p>
  </div>

  <div class="field-card">
    <div class="field-head">
      <span class="field-name"><code>tag</code></span>
      <span class="field-title">برچسب (Tag / Status Tag)</span>
    </div>
    <p>
      این ستون اسکریپت SQL مربوط به <strong>برچسب‌گذاری</strong> محصولات را نگه می‌دارد.
      در کوئری مرجع، این بخش جایگزین بلوک <code>@@tag@@</code> می‌شود
      و به‌صورت یک CTE کامل با نام <code>tagged</code> تعریف می‌شود که خروجی آن
      شامل <code>status_tag</code> و <code>action</code> است.
    </p>
    <p>
      برچسب‌ها بر اساس شاخص‌های <code>rstr</code>، <code>cdr</code>، <code>rvr</code>،
      <code>vt</code>، <code>discount_quality</code>، <code>velocity_gap</code>،
      <code>age_in_months</code>، <code>current_velocity</code>، <code>prior_velocity</code>
      و <code>completed</code> تعیین می‌شوند.
    </p>
    <p>
      مقادیر مجاز <code>status_tag</code> در تعریف پیش‌فرض:
    </p>
    <ul>
      <li><code>موجودی_مرده_کامل</code></li>
      <li><code>موجودی_مرده_مانده</code></li>
      <li><code>زود_تمام_شده</code></li>
      <li><code>متوقف_شده</code></li>
      <li><code>قوی</code></li>
      <li><code>خطر</code></li>
      <li><code>سلامت</code></li>
      <li><code>ضعیف</code></li>
      <li><code>na</code></li>
    </ul>
    <p>
      و مقادیر مجاز <code>action</code> در همان CTE:
    </p>
    <ul>
      <li><code>آرشیو</code></li>
      <li><code>حذف</code></li>
      <li><code>پایان_فصل</code></li>
      <li><code>خرید</code></li>
      <li><code>تحقیق</code></li>
      <li><code>تخفیف_50</code></li>
      <li><code>کنترل</code></li>
      <li><code>تخفیف_30</code></li>
      <li><code>تخفیف_20</code></li>
    </ul>
    <p>
      این مقادیر با مقادیر جدول <code>salesoptimizer.actions</code> (به‌ویژه
      <code>کامل_شده</code> و <code>داده_ناکافی</code>) و همچنین تصمیم‌های
      <code>last_completed</code> و <code>current_active</code> در ارتباط هستند.
      تغییر در زیرخط یا فاصله‌ها باعث می‌شود اتصال‌ها و شرط‌های <code>CASE WHEN</code>
      به‌درستی برقرار نشوند و UI ناسازگار شود.
    </p>
  </div>

  <div class="field-card">
    <div class="field-head">
      <span class="field-name"><code>action</code></span>
      <span class="field-title">اقدام (Action / Final SELECT)</span>
    </div>
    <p>
      این ستون اسکریپت SQL مربوط به بخش <strong>اقدام نهایی</strong> را نگه می‌دارد.
      در کوئری مرجع، این بخش جایگزین بلوک <code>@@action@@</code> در انتهای کوئری می‌شود
      و باید یک SELECT کامل و معتبر با نام مستعار <code>t</code> برای
      CTE <code>tagged</code> تولید کند.
    </p>
    <p>
      ساختار پیش‌فرض شامل موارد زیر است:
    </p>
    <ul>
      <li><code>t.*</code> — تمام ستون‌های CTE <code>tagged</code>.</li>
      <li><code>pc.category_name AS name</code> — نام دستهٔ محصول از
          <code>salesoptimizer.product_categories</code>.</li>
      <li>اطلاعات اقدام فعال جاری از CTE <code>current_active</code>
          (<code>active_action</code>، <code>active_action_start_date</code>،
          <code>active_action_end_date</code>).</li>
      <li>تاریخچهٔ اقدام از <code>action_rollup</code>
          (<code>action_count_total</code>، <code>action_count_measured</code>).</li>
      <li>اطلاعات آخرین اقدام کامل‌شده از <code>last_completed</code>
          (<code>last_action</code>، <code>last_action_verdict</code>،
          <code>last_action_lift</code>، <code>last_action_margin_impact</code>).</li>
      <li><code>actions_remaining</code> — تعداد اقدامات باقی‌مانده بر اساس
          <code>status_tag</code> (<code>موجودی_مرده_کامل</code> → ۲،
          <code>موجودی_مرده_مانده</code> → ۳، در غیر این صورت ۰).</li>
      <li><code>next_recommended_action</code> — اقدام بعدی پیشنهادی بر اساس
          <code>status_tag</code>، <code>action_count_total</code>،
          <code>last_action_verdict</code> و <code>last_action_type</code>.</li>
    </ul>
    <p>
      این SELECT نهایی به چهار جدول/CTE زیر متصل می‌شود:
    </p>
    <p>
      <code>LEFT JOIN salesoptimizer.product_categories pc ON pc.category_code = t.category_code</code><br>
      <code>LEFT JOIN action_rollup ar ON ar.product_code = t.product_code</code><br>
      <code>LEFT JOIN last_completed lc ON lc.product_code = t.product_code AND lc.rn = 1</code><br>
      <code>LEFT JOIN current_active ca ON ca.product_code = t.product_code AND ca.rn = 1</code>
    </p>
    <p>
      مقادیر مجاز <code>last_action_verdict</code> در ساختار <code>next_recommended_action</code>:
      <code>موثر</code>، <code>فاقد_تاثیر</code>، <code>مبهم</code>.
    </p>
    <p>
      این بخش باید همیشه به یک نتیجهٔ معتبر و از پیش تعریف‌شده منتهی شود
      (مثلاً <code>خرید</code>، <code>کنترل</code>، <code>تخفیف_20/30/50</code>،
      <code>حذف</code>، <code>تحقیق</code>، <code>آرشیو</code>، <code>پایان_فصل</code>)
      و نباید ساختار جداول <code>actions</code>، <code>product_categories</code>
      یا CTEهای تعریف‌شده را تغییر دهد.
    </p>
  </div>

  <!-- ==================== READ-ONLY COLUMNS ==================== -->
  <div class="guide-card" style="background:#fff;border:1px dashed #cbd5e1;border-radius:10px;padding:12px 16px;margin:14px 0;">
    <div class="field-head">
      <span class="field-title">📌 ستون‌های محاسبه‌شده (غیرقابل ویرایش)</span>
    </div>
    <p>
      ستون‌های زیر به‌صورت خودکار در <code>CREATE TABLE AS</code> محاسبه می‌شوند و
      در این پنل اسکریپت‌شان نمایش داده نمی‌شود:
    </p>
    <ul>
      <li><code>product_code</code>، <code>category_code</code>، <code>total_inventory</code>،
          <code>first_show_date</code>، <code>age_in_months</code>، <code>age_in_days</code>،
          <code>discount_percentage</code>، <code>total_sold</code>،
          <code>total_sold_12_months</code>، <code>all_time_sold</code>، <code>supplier</code>
          — از جدول <code>twelve_month_analysis</code>.</li>
      <li><code>remaining_inventory</code>، <code>remaining_months</code>،
          <code>cumulative_sell_through</code>، <code>cumulative_qty</code>،
          <code>current_velocity</code>، <code>prior_velocity</code>
          — در <code>product_signals</code>.</li>
      <li><code>benchmark_cumulative_sell_through</code>،
          <code>benchmark_cumulative_qty</code>، <code>benchmark_current_month_qty</code>،
          <code>avg_discount_percentage</code> — در <code>combined</code>.</li>
      <li><code>rstr</code>، <code>cdr</code>، <code>rvr</code>، <code>dd</code>،
          <code>required_future_velocity</code>، <code>velocity_gap</code>،
          <code>completed</code> — در <code>metrics</code>.</li>
      <li><code>name</code>، <code>active_action*</code>، <code>action_count_*</code>،
          <code>last_action*</code>، <code>actions_remaining</code>،
          <code>next_recommended_action</code> — در SELECT نهایی.</li>
    </ul>
  </div>

  <!-- ==================== FULL SQL SCRIPT ==================== -->
  <p style="font-size:13.5px;color:#475569;">
    در ادامه، ساختار کلی اسکریپت <code>analysis.sql</code> با نشانه‌گذاری محل
    بلوک‌های قابل‌ویرایش (<code>@@vt@@</code>، <code>@@discount_quality@@</code>،
    <code>@@tag@@</code>، <code>@@action@@</code>) آورده شده است.
    هرگونه تغییر در نام مقادیر (به‌ویژه مقادیری مانند <code>کامل_شده</code> و
    <code>داده_ناکافی</code>) ممنوع است.
  </p>
  <pre class="code-block" dir="ltr"><code>DROP TABLE IF EXISTS salesoptimizer.analysis_grade_one;

CREATE TABLE salesoptimizer.analysis_grade_one AS
WITH product_signals AS (...),
     benchmark_signals AS (...),
     combined AS (...),
     metrics AS (
        ...
        -- This part can be editted
        @@vt@@
        -- End
        ...
        -- This part can be editted
        @@discount_quality@@
        -- End
     ),
     -- This part can be editted
     @@tag@@
     -- End
     action_rollup AS (...),
     last_completed AS (...),
     current_active AS (...)
     -- this part can be edited
     @@action@@
     -- End
     LEFT JOIN salesoptimizer.product_categories pc ON pc.category_code = t.category_code
     LEFT JOIN action_rollup   ar ON ar.product_code = t.product_code
     LEFT JOIN last_completed  lc ON lc.product_code = t.product_code AND lc.rn = 1
     LEFT JOIN current_active  ca ON ca.product_code = t.product_code AND ca.rn = 1;
</code></pre>

  <div class="guide-reminder">
    <strong>یادآوری نهایی:</strong>
    این ساختار به‌صورت Singleton است و تنها <strong>اولین رکورد</strong> معتبر است.
    برای بازگشت به حالت پیش‌فرض، رکورد اول را حذف کرده و یک رکورد جدید اضافه کنید.
    همواره پیش از ذخیره، صحت نام مقادیر (زیرخط و فاصله‌ها) را بررسی کنید.
  </div>
</div>
"""


@admin.register(Sqlchunk)
class SqlchunkAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "راهنمای پیکربندی موتور SQL",
            {
                "description": mark_safe(GUIDE_HTML),
                "fields": ("vt", "discount_quality", "tag", "action"),
            },
        ),
    )

    formfield_overrides = {
        db_models.TextField: {
            "widget": forms.Textarea(
                attrs={
                    "rows": 15,
                    "cols": 80,
                    "style": "font-family: monospace; font-size: 13px;",
                    "dir": "ltr",
                }
            )
        }
    }