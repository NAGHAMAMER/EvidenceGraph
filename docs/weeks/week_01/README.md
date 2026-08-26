# الأسبوع الأول — تأسيس مشروع EvidenceGraph

## هدف الأسبوع

إنشاء أساس منظم وقابل للتشغيل والاختبار لمشروع EvidenceGraph قبل البدء بجمع الأبحاث وتطبيق NLP والـAgent.

## فكرة المشروع

EvidenceGraph نظام بحث علمي عام متعدد المجالات يقوم بـ:

- البحث عن أوراق علمية من مصادر متعددة.
- معالجة النصوص باستخدام NLP.
- استخراج الادعاءات والأدلة المؤيدة أو المعارضة.
- استخدام Agent لتنظيم خطوات البحث والتحليل.
- بناء رسم بياني يربط الأوراق والادعاءات والأدلة.
- عرض النتائج من خلال واجهة ويب.

## ما تم إنجازه

### 1. تجهيز Docker باستخدام Hyper-V

تم تثبيت Docker Desktop في:

```text
D:\Apps\DockerDesktop
```

ويستخدم Docker حاليًا آلة Linux افتراضية عبر Hyper-V اسمها:

```text
DockerDesktopVM
```

قرصها موجود في:

```text
D:\DockerHyperVData\DockerDesktop.vhdx
```

تم الانتقال من WSL2 إلى Hyper-V بسبب تكرار خطأ ربط قرص WSL بعد إعادة تشغيل Windows.

تم تعطيل WSL وVirtual Machine Platform والإبقاء على Hyper-V.

تم التحقق باستخدام:

```powershell
docker version
docker run --rm hello-world
```

### 2. إنشاء المشروع وGit

مسار المشروع:

```text
D:\AI_Projects\EvidenceGraph
```

تم إنشاء Git محليًا على الفرع:

```text
main
```

### 3. إنشاء بنية المشروع

```text
backend/    FastAPI وNLP والـAgent
frontend/   واجهة React
data/       البيانات الخام والمعالجة
deploy/     ملفات النشر
docs/       التوثيق الأسبوعي
scripts/    الأدوات والسكريبتات
```

### 4. تجهيز الإعدادات والأمان

تم إنشاء:

- `.gitignore` لمنع رفع الأسرار والملفات المؤقتة.
- `.env` للقيم المحلية والأسرار، وهو مستبعد من Git.
- `.env.example` كقالب آمن للإعدادات.
- `config.py` لقراءة الإعدادات والتحقق منها.
- `.editorconfig` لتوحيد تنسيق الملفات.
- `.gitattributes` لتنظيم نهايات الأسطر والترميز.

مسار الإعدادات:

```text
.env → config.py → بقية ملفات Backend
```

### 5. إنشاء FastAPI

تم إنشاء المسارات:

```text
GET /
GET /api/v1/health
GET /docs
GET /redoc
```

`/docs` هي واجهة Swagger التي ينشئها FastAPI تلقائيًا من مسارات API.

### 6. إنشاء Dockerfile متعدد المراحل

يحتوي Dockerfile على:

- `base`: Python والمكتبات الأساسية وكود التطبيق.
- `development`: أدوات الاختبار وملفات tests.
- `production`: التطبيق فقط دون أدوات التطوير.

صورة Python المستخدمة:

```text
python:3.
