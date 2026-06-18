"""
Resume Generator module for Resume-Insight AI.
Uses Groq/Gemini LLM to rewrite resumes to 100% match the job description
and compiles them into professionally designed PDFs using ReportLab.
"""

import json
import logging
import os
from typing import Optional, Dict, Any

# ReportLab imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from src.config.config import LLMConfig

logger = logging.getLogger(__name__)


class HRFlowable(Flowable):
    """Custom Flowable to draw a clean horizontal line separator"""
    def __init__(self, width: float, thickness: float = 1, color: colors.Color = colors.HexColor("#CBD5E1"), space_after: float = 8):
        super().__init__()
        self.width = width
        self.thickness = thickness
        self.color = color
        self.space_after = space_after

    def wrap(self, availWidth, availHeight):
        return self.width, self.thickness + self.space_after

    def draw(self):
        self.canv.saveState()
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.space_after, self.width, self.space_after)
        self.canv.restoreState()


class ResumeGenerator:
    """Handles LLM-driven resume rewriting and professional PDF generation"""
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        self.llm_config = llm_config or LLMConfig()
        self.llm_client = None
        self._initialize_llm_client()

    def _initialize_llm_client(self):
        """Initialize LLM client for rewrite"""
        if not self.llm_config or not self.llm_config.api_key:
            logger.warning("No LLM API Key configured for ResumeGenerator")
            return
        
        provider = self.llm_config.provider.lower()
        try:
            if provider == "groq":
                from groq import Groq
                self.llm_client = Groq(api_key=self.llm_config.api_key, timeout=240.0)
            elif provider == "openai":
                from openai import OpenAI
                self.llm_client = OpenAI(api_key=self.llm_config.api_key, timeout=240.0)
        except Exception as e:
            logger.error(f"Could not initialize LLM client in ResumeGenerator: {e}")

    def generate_matched_resume_json(
        self, 
        resume_text: str, 
        job_description: str,
        matching_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Queries the LLM to rewrite the resume sections to achieve a 100% match with the Job Description.
        Returns a structured JSON matching the resume schema.
        """
        if not self.llm_client:
            raise ValueError("LLM client not initialized. Please configure API keys.")

        missing_skills_str = ", ".join(matching_result.get("missing_skills", []))
        matched_skills_str = ", ".join([m.get("job_skill", m.get("resume_skill", "")) for m in matching_result.get("matched_skills", []) if m])

        prompt = f"""
You are an expert technical recruiter and resume writer.
Your goal is to rewrite the candidate's original resume so it becomes a 100% match to the job description.

Specifically:
1. Identify and preserve the original contact details (name, email, phone, location, links). Do NOT change them.
2. Group the technical skills into categories: languages, frameworks_libraries, tools_databases, and other_skills.
3. Integrate ALL of the following missing skills into the skills list: {missing_skills_str}
4. Modify the professional experience bullet points to weave in these missing skills and demonstrate how they align with the job description.
5. Do NOT invent new jobs, change dates, change company names, or modify education degrees. Keep those exactly as in the original resume.
6. Make sure the output is a highly polished, professional resume representation.

Original Resume Text:
\"\"\"{resume_text}\"\"\"

Job Description:
\"\"\"{job_description}\"\"\"

Target Missing Skills to integrate:
{missing_skills_str}

Already Matched Skills:
{matched_skills_str}

Response Format:
You MUST return ONLY a valid JSON object matching the following schema, with no markdown code blocks, no additional explanation, and no extra characters. Every key must exist.

{{
  "personal_info": {{
    "name": "Candidate's full name",
    "email": "Email address",
    "phone": "Phone number",
    "location": "City, State or Country",
    "linkedin": "LinkedIn profile link or empty string",
    "github": "GitHub profile link or empty string",
    "website": "Personal portfolio link or empty string"
  }},
  "summary": "A professional summary tailored to the job description highlighting relevant experience and key skills.",
  "skills": {{
    "languages": ["Programming Language 1", "Language 2"],
    "frameworks_libraries": ["Framework 1", "Library 2"],
    "tools_databases": ["Tool 1", "Database 2"],
    "other_skills": ["Methodology 1", "Soft Skill 2"]
  }},
  "experience": [
    {{
      "company": "Company Name",
      "position": "Job Title",
      "duration": "Start Date - End Date",
      "location": "City, State or Remote",
      "bullets": [
        "Tailored achievement bullet point 1 integrating key skills and matching JD responsibilities.",
        "Tailored achievement bullet point 2 demonstrating impact."
      ]
    }}
  ],
  "education": [
    {{
      "institution": "University/School Name",
      "degree": "Degree earned (e.g. B.S. in Computer Science)",
      "duration": "Graduation date or range",
      "location": "City, State"
    }}
  ],
  "projects": [
    {{
      "title": "Project Title",
      "duration": "Date/Range",
      "description": "Tailored project description highlighting relevant technologies and outcomes."
    }}
  ]
}}
"""
        response = self.llm_client.chat.completions.create(
            model=self.llm_config.model or "llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
        )
        content = response.choices[0].message.content.strip()

        # Clean markdown code blocks
        if content.startswith("```"):
            lines = content.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()

        try:
            resume_data = json.loads(content)
            return resume_data
        except Exception as e:
            logger.error(f"Failed to parse LLM resume rewrite response as JSON: {e}\nRaw output: {content}")
            raise ValueError("Failed to generate a valid resume JSON structure from LLM.")

    def generate_resume_pdf(self, resume_data: Dict[str, Any], output_path: str):
        """
        Compiles the structured resume JSON into a beautiful, professional PDF resume using ReportLab Platypus.
        """
        # Page size and document setup
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=36,  # 0.5 inch margins
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Color palette
        c_primary = colors.HexColor("#1A365D")   # Deep Slate Navy
        c_text = colors.HexColor("#1E293B")      # Dark Charcoal
        c_subtext = colors.HexColor("#475569")   # Muted Slate
        c_line = colors.HexColor("#CBD5E1")      # Slate border/divider

        # Define custom styles
        style_name = ParagraphStyle(
            'ResumeName',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=c_primary,
            alignment=1,  # Centered
            spaceAfter=4
        )

        style_contact = ParagraphStyle(
            'ResumeContact',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=c_subtext,
            alignment=1,  # Centered
            spaceAfter=8
        )

        style_summary = ParagraphStyle(
            'ResumeSummary',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=c_text,
            spaceAfter=8
        )

        style_sec_title = ParagraphStyle(
            'ResumeSecTitle',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=c_primary,
            spaceBefore=10,
            spaceAfter=2,
            keepWithNext=True
        )

        style_job_title = ParagraphStyle(
            'ResumeJobTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
            textColor=c_text
        )

        style_job_org = ParagraphStyle(
            'ResumeJobOrg',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=9.5,
            leading=12,
            textColor=c_subtext
        )

        style_bullet = ParagraphStyle(
            'ResumeBullet',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12.5,
            textColor=c_text,
            leftIndent=12,
            firstLineIndent=-8,
            spaceAfter=2
        )

        style_skill_cat = ParagraphStyle(
            'ResumeSkillCat',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=12,
            textColor=c_text
        )

        style_skill_list = ParagraphStyle(
            'ResumeSkillList',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=c_text
        )

        story = []
        width_content = 540  # 612 (letter width) - 72 (margins)

        # Header Section
        pi = resume_data.get("personal_info", {})
        story.append(Paragraph(pi.get("name", "Candidate Name"), style_name))
        
        # Build contact info string
        contact_parts = []
        if pi.get("email"): contact_parts.append(pi.get("email"))
        if pi.get("phone"): contact_parts.append(pi.get("phone"))
        if pi.get("location"): contact_parts.append(pi.get("location"))
        if pi.get("linkedin"): contact_parts.append(pi.get("linkedin"))
        if pi.get("github"): contact_parts.append(pi.get("github"))
        if pi.get("website"): contact_parts.append(pi.get("website"))
        
        contact_str = "  |  ".join(contact_parts)
        story.append(Paragraph(contact_str, style_contact))

        # Summary Section
        summary = resume_data.get("summary")
        if summary:
            story.append(Paragraph("PROFESSIONAL SUMMARY", style_sec_title))
            story.append(HRFlowable(width_content, thickness=1, color=c_primary, space_after=4))
            story.append(Paragraph(summary, style_summary))

        # Skills Section
        skills = resume_data.get("skills", {})
        if skills:
            story.append(Paragraph("TECHNICAL SKILLS", style_sec_title))
            story.append(HRFlowable(width_content, thickness=1, color=c_primary, space_after=4))
            
            skills_table_data = []
            categories = [
                ("Languages", "languages"),
                ("Frameworks & Libraries", "frameworks_libraries"),
                ("Tools & Databases", "tools_databases"),
                ("Other Competencies", "other_skills")
            ]
            
            for label, key in categories:
                items = skills.get(key, [])
                if items:
                    skills_table_data.append([
                        Paragraph(f"{label}:", style_skill_cat),
                        Paragraph(", ".join(items), style_skill_list)
                    ])
            
            if skills_table_data:
                # Left column takes 140 points, right takes rest (400 points)
                skills_table = Table(skills_table_data, colWidths=[140, 400])
                skills_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                    ('TOPPADDING', (0,0), (-1,-1), 2),
                ]))
                story.append(skills_table)
                story.append(Spacer(1, 4))

        # Professional Experience Section
        experience = resume_data.get("experience", [])
        if experience:
            story.append(Paragraph("PROFESSIONAL EXPERIENCE", style_sec_title))
            story.append(HRFlowable(width_content, thickness=1, color=c_primary, space_after=4))
            
            for job in experience:
                # Job Header (two columns: left is company & position, right is duration & location)
                left_cell = [
                    Paragraph(f"<b>{job.get('company')}</b>", style_job_title),
                    Paragraph(job.get('position', ''), style_job_org)
                ]
                right_cell = [
                    Paragraph(f"<font color='{c_subtext.hexval()}'>{job.get('duration', '')}</font>", ParagraphStyle('RDuration', parent=style_job_title, alignment=2)),
                    Paragraph(f"<font color='{c_subtext.hexval()}'>{job.get('location', '')}</font>", ParagraphStyle('RLocation', parent=style_job_org, alignment=2))
                ]
                
                header_table = Table([[left_cell, right_cell]], colWidths=[320, 220])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                    ('TOPPADDING', (0,0), (-1,-1), 4),
                ]))
                
                job_story = [header_table]
                
                # Bullet points
                for bullet in job.get("bullets", []):
                    job_story.append(Paragraph(f"&bull; {bullet}", style_bullet))
                
                job_story.append(Spacer(1, 4))
                # Keep job header and bullets together on the same page where possible
                story.append(KeepTogether(job_story))

        # Education Section
        education = resume_data.get("education", [])
        if education:
            story.append(Paragraph("EDUCATION", style_sec_title))
            story.append(HRFlowable(width_content, thickness=1, color=c_primary, space_after=4))
            
            for edu in education:
                left_cell = [
                    Paragraph(f"<b>{edu.get('institution')}</b>", style_job_title),
                    Paragraph(edu.get('degree', ''), style_job_org)
                ]
                right_cell = [
                    Paragraph(f"<font color='{c_subtext.hexval()}'>{edu.get('duration', '')}</font>", ParagraphStyle('EDuration', parent=style_job_title, alignment=2)),
                    Paragraph(f"<font color='{c_subtext.hexval()}'>{edu.get('location', '')}</font>", ParagraphStyle('ELocation', parent=style_job_org, alignment=2))
                ]
                
                edu_table = Table([[left_cell, right_cell]], colWidths=[320, 220])
                edu_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                    ('TOPPADDING', (0,0), (-1,-1), 4),
                ]))
                story.append(edu_table)
                story.append(Spacer(1, 4))

        # Projects Section
        projects = resume_data.get("projects", [])
        if projects:
            story.append(Paragraph("PROJECTS & PORTFOLIO", style_sec_title))
            story.append(HRFlowable(width_content, thickness=1, color=c_primary, space_after=4))
            
            for proj in projects:
                left_cell = Paragraph(f"<b>{proj.get('title')}</b>", style_job_title)
                right_cell = Paragraph(f"<font color='{c_subtext.hexval()}'>{proj.get('duration', '')}</font>", ParagraphStyle('PDuration', parent=style_job_title, alignment=2))
                
                proj_table = Table([[left_cell, right_cell]], colWidths=[360, 180])
                proj_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                    ('TOPPADDING', (0,0), (-1,-1), 4),
                ]))
                
                proj_story = [
                    proj_table,
                    Paragraph(proj.get("description", ""), style_bullet),
                    Spacer(1, 4)
                ]
                story.append(KeepTogether(proj_story))

        # Build PDF
        doc.build(story)
