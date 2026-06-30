import re
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dsa_platform.settings")
django.setup()

from roadmap.models import Topic, DayContent, Question

filepath = r"C:\Users\atulg\.gemini\antigravity-ide\brain\263b931e-c325-47d9-a0ef-cfc46e58416b\.system_generated\steps\45\content.md"

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()
line = lines[41]

# Clear existing data
Topic.objects.all().delete()
DayContent.objects.all().delete()
Question.objects.all().delete()

allocated_days_list = [7, 1, 7, 6, 3, 6, 5, 3, 6, 3, 3, 3, 8, 3, 10, 11, 2, 2]

chunks = line.split(r'\"category_name\":\"')
topic_order = 1
global_day = 1

for i, chunk in enumerate(chunks[1:]):
    cat_name = chunk.split(r'\"', 1)[0].replace('\\"', '"')
    cat_name = cat_name.replace(r'\u003e', '>').replace(r'\u0026', '&')
    
    alloc_days = allocated_days_list[i] if i < len(allocated_days_list) else 5
    
    topic = Topic.objects.create(name=cat_name, allocated_days=alloc_days, order=topic_order)
    topic_order += 1
    
    sub_chunks = chunk.split(r'\"subcategory_name\":\"')
    for sub_chunk in sub_chunks[1:]:
        sub_name = sub_chunk.split(r'\"', 1)[0].replace('\\"', '"')
        sub_name = sub_name.replace(r'\u003e', '>').replace(r'\u0026', '&')
        
        day_content = DayContent.objects.create(
            topic=topic,
            day_number=global_day,
            name=sub_name
        )
        global_day += 1
        
        problems_str_match = re.search(r'\\"problems\\":\[(.*?)\]\}', sub_chunk)
        if problems_str_match:
            problems_str = problems_str_match.group(1)
            prob_matches = re.finditer(r'\{.*?\}', problems_str)
            q_order = 1
            for p_match in prob_matches:
                p_str = p_match.group(0)
                def get_field(field):
                    m = re.search(r'\\"' + field + r'\\":\\"(.*?)\\"', p_str)
                    if m:
                        val = m.group(1).replace('\\"', '"')
                        val = val.replace(r'\u0026', '&').replace(r'\u003e', '>')
                        return val
                    return ""
                    
                name = get_field('problem_name')
                article = get_field('article')
                youtube = get_field('youtube')
                leetcode = get_field('leetcode')
                difficulty = get_field('difficulty')
                
                if article == '$undefined': article = ''
                if youtube == '$undefined': youtube = ''
                if leetcode == '$undefined': leetcode = ''
                
                if name:
                    Question.objects.create(
                        day=day_content,
                        name=name,
                        difficulty=difficulty,
                        article_link=article,
                        youtube_link=youtube,
                        leetcode_link=leetcode,
                        order=q_order
                    )
                    q_order += 1

print(f"Database seeded with {Topic.objects.count()} Topics, {DayContent.objects.count()} Days, and {Question.objects.count()} Questions.")
