import os

file_path = r"c:\Users\atulg\OneDrive\Desktop\DSA Course 90\roadmap\templates\roadmap\dashboard.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Title and remove problems count
target_title = """<h4 class="text-navy dark:text-ice text-navy dark:text-ice font-bold text-lg transition-colors">Day {{ day.day_number }}: {% if day.day_obj %}{{ day.day_obj.topic_name }}{% else %}Basics{% endif %}</h4>
                                <p class="text-xs text-slate dark:text-slate-light text-slate dark:text-slate-light font-medium mt-0.5 transition-colors">0 / 10 PROBLEMS</p>"""
replace_title = """<h4 class="text-navy dark:text-ice text-navy dark:text-ice font-bold text-lg transition-colors">Day {{ day.day_number }}</h4>"""
content = content.replace(target_title, replace_title)

# 2. Update Progress Percentage Text
target_progress = """<span class="text-sm font-black text-navy dark:text-ice text-navy dark:text-ice italic transition-colors">0%</span>"""
replace_progress = """<span class="text-sm font-black text-navy dark:text-ice italic transition-colors" id="progress-text-{{ day.day_number }}">{{ day.progress_percentage|default:"0"|floatformat:"0" }}%</span>"""
content = content.replace(target_progress, replace_progress)

# 3. Add checkboxes to 4 categories
target_dsa = """<i class="fa-solid fa-chevron-right ml-auto text-xs text-slate-400 group-hover:text-blue transition-colors"></i>"""
replace_dsa = """<div class="task-checkbox ml-auto flex items-center justify-center w-7 h-7 rounded-full border-2 transition-all cursor-pointer {% if day.tracker.dsa_completed %}bg-blue border-blue text-white{% else %}border-slate-300 dark:border-slate-700 text-transparent hover:border-blue{% endif %}" data-day="{{ day.day_number }}" data-task="dsa_completed"><i class="fa-solid fa-check text-xs"></i></div>"""

target_apt = """<i class="fa-solid fa-chevron-right ml-auto text-xs text-slate-400 group-hover:text-emerald-500 transition-colors"></i>"""
replace_apt = """<div class="task-checkbox ml-auto flex items-center justify-center w-7 h-7 rounded-full border-2 transition-all cursor-pointer {% if day.tracker.aptitude_completed %}bg-emerald-500 border-emerald-500 text-white{% else %}border-slate-300 dark:border-slate-700 text-transparent hover:border-emerald-500{% endif %}" data-day="{{ day.day_number }}" data-task="aptitude_completed"><i class="fa-solid fa-check text-xs"></i></div>"""

target_core = """<i class="fa-solid fa-chevron-right ml-auto text-xs text-slate-400 group-hover:text-purple-500 transition-colors"></i>"""
replace_core = """<div class="task-checkbox ml-auto flex items-center justify-center w-7 h-7 rounded-full border-2 transition-all cursor-pointer {% if day.tracker.core_completed %}bg-purple-500 border-purple-500 text-white{% else %}border-slate-300 dark:border-slate-700 text-transparent hover:border-purple-500{% endif %}" data-day="{{ day.day_number }}" data-task="core_completed"><i class="fa-solid fa-check text-xs"></i></div>"""

target_web = """<i class="fa-solid fa-chevron-right ml-auto text-xs text-slate-400 group-hover:text-orange-500 transition-colors"></i>"""
replace_web = """<div class="task-checkbox ml-auto flex items-center justify-center w-7 h-7 rounded-full border-2 transition-all cursor-pointer {% if day.tracker.web_dev_completed %}bg-orange-500 border-orange-500 text-white{% else %}border-slate-300 dark:border-slate-700 text-transparent hover:border-orange-500{% endif %}" data-day="{{ day.day_number }}" data-task="web_dev_completed"><i class="fa-solid fa-check text-xs"></i></div>"""

content = content.replace(target_dsa, replace_dsa)
content = content.replace(target_apt, replace_apt)
content = content.replace(target_core, replace_core)
content = content.replace(target_web, replace_web)

# 4. Add JS code
js_code = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.task-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const dayNumber = this.getAttribute('data-day');
            const taskName = this.getAttribute('data-task');
            
            fetch("{% url 'toggle_task_completion' %}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: JSON.stringify({
                    'day_number': dayNumber,
                    'task_name': taskName
                })
            })
            .then(response => response.json())
            .then(data => {
                if(data.success) {
                    if (data.completed) {
                        this.classList.remove('border-slate-300', 'dark:border-slate-700', 'text-transparent');
                        if(taskName === 'dsa_completed') this.classList.add('bg-blue', 'border-blue', 'text-white');
                        else if(taskName === 'aptitude_completed') this.classList.add('bg-emerald-500', 'border-emerald-500', 'text-white');
                        else if(taskName === 'core_completed') this.classList.add('bg-purple-500', 'border-purple-500', 'text-white');
                        else if(taskName === 'web_dev_completed') this.classList.add('bg-orange-500', 'border-orange-500', 'text-white');
                    } else {
                        this.classList.remove('bg-blue', 'border-blue', 'text-white', 'bg-emerald-500', 'border-emerald-500', 'bg-purple-500', 'border-purple-500', 'bg-orange-500', 'border-orange-500');
                        this.classList.add('border-slate-300', 'dark:border-slate-700', 'text-transparent');
                    }
                    const progressText = document.getElementById('progress-text-' + dayNumber);
                    if (progressText) progressText.textContent = Math.round(data.progress_percentage) + '%';
                }
            });
        });
    });
});
</script>
{% endblock %}
"""

# Replace the LAST endblock
parts = content.rsplit("{% endblock %}", 1)
content = js_code.join(parts)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Dashboard updated successfully.")
