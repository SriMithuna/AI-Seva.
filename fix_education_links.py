from pathlib import Path

path = Path("departments/education/templates/education/index.html")
content = path.read_text(encoding="utf-8")

# Remove the misplaced service button from the scheme section
wrong_button = '''              <a class="official-link"
                 href="{% url 'education_apply' service.id %}">
                 Access Service →
              </a>
'''

if wrong_button not in content:
    raise SystemExit("Misplaced button not found. No changes made.")

content = content.replace(wrong_button, "", 1)

# Add the service button inside the actual services loop
service_marker = '''                  <span class="service-label"> Education Service </span>
                </div>
              </div>
            </article>'''

service_replacement = '''                  <span class="service-label"> Education Service </span>
                </div>
              </div>

              <a class="official-link"
                 href="{% url 'education_apply' service.id %}">
                 Access Service →
              </a>
            </article>'''

if service_marker not in content:
    raise SystemExit("Service section not found. No changes made.")

content = content.replace(service_marker, service_replacement, 1)

path.write_text(content, encoding="utf-8")
print("Education links corrected successfully!")