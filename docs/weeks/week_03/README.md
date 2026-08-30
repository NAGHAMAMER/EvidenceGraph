# الأسبوع الثالث — البحث الدلالي متعدد اللغات

## هدف الأسبوع

إضافة أول مرحلة NLP فعلية إلى EvidenceGraph، بحيث لا يكتفي النظام بالبحث بالكلمات المفتاحية، بل يعيد ترتيب الأوراق العلمية بحسب التشابه الدلالي بين سؤال المستخدم ومحتوى الأوراق.

## النتيجة العامة

أصبح EvidenceGraph قادرًا على:

- البحث في OpenAlex وCrossref.
- دمج النتائج وحذف الأوراق المكررة.
- تحويل السؤال والأوراق إلى Embeddings.
- حساب التشابه الدلالي.
- ترتيب الأوراق من الأكثر ارتباطًا إلى الأقل.
- دعم الاستعلامات العربية والإنجليزية.
- عرض النتائج ودرجات التشابه من خلال Swagger.

## 1. إضافة مكتبات NLP

تمت إضافة المكتبات التالية:

```text
fastembed==0.8.0
numpy==2.5.2
```

### FastEmbed

تُستخدم لتشغيل نموذج Embeddings محليًا باستخدام ONNX، دون الحاجة إلى إرسال النصوص إلى خدمة ذكاء اصطناعي خارجية.

### NumPy

تُستخدم للتعامل مع المتجهات وتنفيذ العمليات الرياضية، ومنها حساب Cosine Similarity.

تم اختيار FastEmbed لأنه أخف من المكتبات التي تعتمد على PyTorch، مما يجعله أنسب لجهاز التطوير وللنشر السحابي المجاني.

## 2. نموذج Embeddings متعدد اللغات

النموذج المستخدم هو:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

خصائص النموذج:

- يدعم أكثر من 50 لغة، ومنها العربية والإنجليزية.
- يحول كل نص إلى متجه بطول 384 قيمة.
- يدعم مقارنة نصوص مكتوبة بلغات مختلفة.
- يعمل محليًا داخل Docker.
- مناسب للتشابه الدلالي والبحث الدلالي.

يتم تحديد النموذج من خلال:

```env
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

## 3. تخزين النموذج بشكل دائم

تم إنشاء Docker Volume باسم:

```text
evidencegraph_embedding_models
```

ويُربط داخل حاوية API بالمسار:

```text
/models
```

ويحفظ FastEmbed النموذج داخل:

```text
/models/fastembed
```

إعداد Compose المستخدم:

```yaml
services:
  api:
    volumes:
      - embedding_models:/models

volumes:
  embedding_models:
```

فائدة هذا الربط هي الاحتفاظ بملفات النموذج بعد إعادة إنشاء الحاوية، وعدم تنزيله من Hugging Face في كل مرة.

تمت إضافة إعدادات تنزيل Hugging Face التالية:

```env
HF_HUB_DISABLE_XET=1
HF_HUB_DOWNLOAD_TIMEOUT=600
```

تُستخدم هذه الإعدادات لتجنب مشكلة Xet/CAS وإعطاء الملفات وقتًا أطول للتنزيل عند بطء الاتصال.

## 4. إنشاء خدمة Embeddings

تم إنشاء الملف:

```text
backend/app/nlp/embeddings.py
```

تتضمن الخدمة الوظائف التالية:

### تحميل النموذج

يتم تحميل النموذج عند أول استخدام فقط باستخدام Lazy Loading، حتى لا يستهلك الذاكرة بمجرد تشغيل API.

### تحويل نص واحد

```python
embed_text(text)
```

تحول نصًا واحدًا إلى متجه بطول 384 قيمة.

### تحويل عدة نصوص

```python
embed_texts(texts)
```

تحول مجموعة نصوص إلى مصفوفة متجهات دفعة واحدة.

إذا أدخلنا ثلاثة نصوص، يكون شكل الناتج:

```text
(3, 384)
```

### حساب التشابه

```python
cosine_similarities(query_vector, document_vectors)
```

تحسب درجة التشابه بين متجه السؤال ومتجهات الأوراق.

### إعادة استخدام الخدمة

يتم استخدام `lru_cache` لإعادة استخدام نسخة واحدة من خدمة Embeddings بدل إنشاء النموذج وتحميله عدة مرات داخل العملية نفسها.

## 5. حساب Cosine Similarity

تُحسب درجة التشابه وفق المعادلة:

```text
dot(query, document)
--------------------------------
norm(query) × norm(document)
```

تتراوح النتيجة بين:

```text
-1 و 1
```

كلما اقتربت النتيجة من `1` كان التشابه الدلالي أعلى.

الحقل:

```json
"semantic_score": 0.91
```

لا يمثل احتمالًا أو نسبة دقة، بل يمثل درجة التشابه بين السؤال والورقة.

## 6. إنشاء نموذج الورقة المرتبة

تمت إضافة:

```text
RankedPaper
```

وهو مبني على نموذج `Paper` نفسه، مع إضافة:

```python
semantic_score: float
```

كما تمت إضافة:

```text
SemanticPaperSearchResponse
```

وتتضمن الاستجابة:

```text
query
total
returned
providers
papers
```

## 7. إنشاء خدمة الترتيب الدلالي

تم إنشاء:

```text
backend/app/services/semantic_ranking.py
```

تقوم الخدمة بالخطوات التالية:

1. جمع عنوان الورقة وملخصها وموضوعاتها.
2. تحويل سؤال المستخدم إلى Embedding.
3. تحويل الأوراق المرشحة إلى Embeddings.
4. حساب Cosine Similarity.
5. إضافة `semantic_score` إلى كل ورقة.
6. ترتيب الأوراق من أعلى درجة إلى أقل درجة.
7. إعادة العدد المطلوب فقط.

مسار التنفيذ:

```text
السؤال + الأوراق
        ↓
Embeddings
        ↓
Cosine Similarity
        ↓
ترتيب دلالي
```

## 8. إنشاء خدمة البحث الدلالي المجمعة

تم إنشاء:

```text
backend/app/services/semantic_search.py
```

تربط هذه الخدمة بين البحث التقليدي والترتيب الدلالي:

```text
PaperSearchService
        ↓
OpenAlex + Crossref
        ↓
دمج النتائج وحذف التكرار
        ↓
SemanticRankingService
        ↓
أفضل النتائج دلاليًا
```

إذا طلب المستخدم أربع أوراق، يجلب النظام عددًا أكبر من المرشحين:

```text
candidate_limit = limit × 3
```

ثم يعيد ترتيبهم ويختار أفضل أربع أوراق.

الحد الأعلى لعدد المرشحين هو:

```text
50
```

تم تشغيل عملية الترتيب باستخدام:

```python
asyncio.to_thread
```

حتى لا تمنع عملية حساب Embeddings خادم FastAPI من التعامل مع طلبات أخرى.

## 9. إنشاء Semantic Search API

تم إنشاء الملف:

```text
backend/app/api/routes/semantic_search.py
```

وتمت إضافة المسار:

```text
GET /api/v1/papers/semantic-search
```

المعاملات:

```text
query: سؤال البحث
limit: عدد النتائج المطلوبة من 1 إلى 20
```

يمكن تجربة المسار من Swagger:

```text
http://localhost:8000/docs
```

## 10. دعم اللغات

لا يفرض الكود قائمة لغات محددة.

المعامل:

```python
query: str
```

يقبل نصوص Unicode، ولذلك يمكن إرسال استعلامات بالعربية والإنجليزية ولغات أخرى.

تعتمد جودة المرشحين الأوليين على الأوراق التي يستطيع OpenAlex وCrossref العثور عليها بلغة السؤال.

بعد جلب المرشحين، يستخدم النظام نموذج Embeddings متعدد اللغات لإعادة ترتيب النتائج.

## 11. تجربة عربية حقيقية

تم اختبار السؤال:

```text
استخدام الذكاء الاصطناعي للكشف المبكر عن سرطان الثدي
```

وكانت النتيجة:

```text
total: 15
returned: 5
providers: OpenAlex وCrossref
أعلى semantic_score: 0.7589
```

ظهرت نتائج مرتبطة بالكشف المبكر عن سرطان الثدي، كما ظهرت ورقة بعنوان إنجليزي وملخص عربي، مما أكد عمل النموذج مع أكثر من لغة.

ظهرت أيضًا بعض النتائج الأقل ارتباطًا، لأنها تشترك مع السؤال في عبارات عامة مثل الذكاء الاصطناعي والكشف المبكر.

## 12. تجربة إنجليزية حقيقية

تم اختبار السؤال:

```text
artificial intelligence for early breast cancer detection
```

وكانت النتيجة:

```text
total: 28
returned: 5
providers: OpenAlex وCrossref
أعلى semantic_score: 0.9677
```

كانت النتائج الإنجليزية أكثر دقة، لأن المصادر العلمية تحتوي عددًا أكبر من الأوراق والبيانات الوصفية باللغة الإنجليزية.

## 13. تفسير اختلاف النتائج بين اللغات

يستطيع نموذج Embeddings مقارنة اللغات، لكن الترتيب الدلالي يعمل على الأوراق التي جلبتها المصادر فقط.

```text
السؤال
  ↓
OpenAlex وCrossref
  ↓
مجموعة الأوراق المرشحة
  ↓
الترتيب الدلالي
```

إذا لم يجلب المصدر ورقة معينة، فلا يستطيع Semantic Ranking إضافتها لاحقًا.

سيعالج Agent في الأسبوع الرابع هذه المشكلة عن طريق البحث بالسؤال الأصلي وبصيغة إنجليزية مكافئة، ثم دمج النتائج وترتيبها.

## 14. اختبارات الأسبوع الثالث

تم إنشاء الملفات:

```text
backend/tests/test_embeddings.py
backend/tests/test_semantic_ranking.py
backend/tests/test_semantic_search.py
backend/tests/test_semantic_search_api.py
```

تغطي الاختبارات:

- تحويل نص واحد إلى متجه.
- تحويل عدة نصوص.
- تنظيف النصوص.
- رفض النصوص الفارغة.
- حساب Cosine Similarity.
- التعامل مع المتجه الصفري.
- رفض اختلاف أبعاد المتجهات.
- بناء النص المستخدم لتمثيل الورقة.
- ترتيب الأوراق بحسب التشابه.
- تطبيق `limit` بعد الترتيب.
- إرجاع قائمة فارغة عند عدم وجود أوراق.
- جلب عدد إضافي من المرشحين.
- تطبيق الحد الأعلى البالغ 50 مرشحًا.
- اختبار Semantic Search API.
- التحقق من مدخلات API.

تستخدم اختبارات الوحدة نماذج وهمية، حتى تكون سريعة ولا تعتمد على الإنترنت أو تنزيل النموذج الحقيقي.

النتيجة النهائية:

```text
29 passed
```

## 15. الملفات المضافة

```text
backend/app/api/routes/semantic_search.py
backend/app/nlp/embeddings.py
backend/app/services/semantic_ranking.py
backend/app/services/semantic_search.py
backend/tests/test_embeddings.py
backend/tests/test_semantic_ranking.py
backend/tests/test_semantic_search.py
backend/tests/test_semantic_search_api.py
docs/weeks/week_03/README.md
```

## 16. الملفات المعدلة

```text
.env.example
backend/app/api/routes/papers.py
backend/app/core/config.py
backend/app/main.py
backend/app/schemas/paper.py
backend/app/services/paper_search.py
backend/requirements.txt
compose.yaml
```

## 17. أوامر التحقق

```powershell
docker compose config
docker compose ps
docker compose exec -T api python -m pytest -q
git diff --check
```

## حدود النسخة الحالية

- جودة النتائج الأولية تعتمد على لغة البيانات المتوفرة في OpenAlex وCrossref.
- لا توجد حاليًا ترجمة أو توسعة تلقائية للسؤال.
- يعيد النظام ترتيب النتائج ولا يستخرج الادعاءات والأدلة بعد.
- لا توجد واجهة Frontend حتى الآن.
- لا تمثل `semantic_score` احتمالًا أو نسبة دقة.

## نتيجة الأسبوع الثالث

اكتملت مرحلة البحث الدلالي متعدد اللغات بنجاح.

أصبح EvidenceGraph قادرًا على البحث في مصدرين علميين، ودمج النتائج، وحذف التكرار، وتحويل السؤال والأوراق إلى Embeddings، وحساب التشابه، وإعادة ترتيب النتائج، وعرضها من خلال Swagger.

الخطوة التالية هي بناء Agent ينظم البحث متعدد اللغات، ويستخرج الادعاءات والأدلة، ويمهد لبناء Evidence Graph.
