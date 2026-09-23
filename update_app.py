import os
import re

app_path = r"c:\Users\Student\Desktop\Humangait_FYP\Frontend\src\App.tsx"

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Terminology replacements
content = re.sub(r'interface Subject \{', r'interface Person {', content)
content = re.sub(r'MOCK_SUBJECTS:\s*Subject\[\]', r'MOCK_PERSONS: Person[]', content)
content = re.sub(r'Subject Registry', r'Person Registry', content)
content = re.sub(r'SUBJECT REGISTRY', r'PERSON REGISTRY', content)
content = re.sub(r'Subject identified', r'Person identified', content)
content = re.sub(r'subject identity', r'person identity', content)
content = re.sub(r'Identified Subject', r'Identified Person', content)
content = re.sub(r'Recent Subjects', r'Recent Persons', content)
content = re.sub(r'Dataset Subjects', r'Dataset Persons', content)
content = re.sub(r'Enroll New Subject', r'Enroll New Person', content)
content = re.sub(r'Predicted Subject', r'Predicted Person', content)
content = re.sub(r'MOCK_SUBJECTS', r'MOCK_PERSONS', content)

# Update variables 'subject.' to 'person.' and '(subject)' to '(person)'
content = re.sub(r'\bsubject\.', r'person.', content)
content = re.sub(r'\(subject\)', r'(person)', content)
content = re.sub(r'\{subject\}', r'{person}', content)

# 2. Under Dashboard and Engine Heading remove block completely containing (+0.4%, Model Accuracy, 98.7% Validation)
# Make it flexible in case of different indentation
dashboard_stat_block = r'''<div className="grid grid-cols-1 md:grid-cols-3 gap-6">\s*<StatCard label="Model Accuracy" value="98.7%" subValue="Validation" icon=\{ShieldCheck\} trend=\{0.4\} />\s*</div>'''
content = re.sub(dashboard_stat_block, '', content)

# 3. MOCK_ACCURACY_DATA replacement
old_mock_accuracy = r'''const MOCK_ACCURACY_DATA = \[\s*\{\s*condition:\s*'Normal',\s*accuracy:\s*98.7\s*\},.*?\];'''
new_mock_accuracy = r'''const MOCK_ACCURACY_DATA = [
  { condition: 'Normal(Training set)', accuracy: 99.99 },
  { condition: 'Bag', accuracy: 97.9 },
  { condition: 'Coat', accuracy: 30.65 },
];'''
content = re.sub(old_mock_accuracy, new_mock_accuracy, content, flags=re.DOTALL)

# 4. Upload Video Frames button onClick mapping
old_button = r'''<button className="flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-sm transition-all shadow-lg shadow-indigo-500/20">\s*<Upload className="w-4 h-4" />\s*Upload Video Frames\s*</button>'''
new_button = r'''<button onClick={open} className="flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-sm transition-all shadow-lg shadow-indigo-500/20">
                    <Upload className="w-4 h-4" />
                    Upload Video Frames
                  </button>'''
content = re.sub(old_button, new_button, content)

# 5. Background image replace
content = content.replace(r'src="https://picsum.photos/seed/gait/1280/720"', r'src="/background.png"')

# 6. Person Registry 30 items
old_mock_subjects = r'''const MOCK_PERSONS: Person\[\] = \[\s*\{ id: 'SUB-01'.*?\];'''
new_mock_persons = r'''const MOCK_PERSONS: Person[] = Array.from({ length: 30 }, (_, i) => {
  const num = (i + 1).toString().padStart(3, '0');
  return {
    id: num,
    name: `Person ${i + 1}`,
    label: num,
    dataset: 'FYP Dataset',
    status: 'active' as const,
    avatar: `https://api.dicebear.com/7.x/bottts-neutral/svg?seed=${num}`,
    lastSeen: 'Recently'
  };
});'''
content = re.sub(old_mock_subjects, new_mock_persons, content, flags=re.DOTALL)

# Replace '5 Enrolled Profiles' with '30 Enrolled Profiles'
content = content.replace('5 Enrolled Profiles', '30 Enrolled Profiles')

# 7. Remove Log ID table
sidebar_logs = r'''<SidebarItem\s*icon=\{History\}\s*label="Accuracy History"\s*active=\{activeView === 'logs'\}\s*onClick=\{.*?\}\s*/>'''
content = re.sub(sidebar_logs, '', content)

content = re.sub(r'\{\s*activeView === \'logs\' && \(.*?\}\s*</motion\.div>\s*\)\s*\}\s*</AnimatePresence>', '\n          </AnimatePresence>', content, flags=re.DOTALL)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated App.tsx successfully.")
