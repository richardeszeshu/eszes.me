import os
from PIL import Image as PILImage, ImageDraw
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase.pdfmetrics import registerFontFamily

def register_custom_fonts():
    font_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
    r_path = os.path.join(font_dir, "Arial-Regular.ttf")
    b_path = os.path.join(font_dir, "Arial-Bold.ttf")
    i_path = os.path.join(font_dir, "Arial-Italic.ttf")
    bi_path = os.path.join(font_dir, "Arial-BoldItalic.ttf")

    if not (os.path.exists(r_path) and os.path.exists(b_path)):
        sys_r = "/System/Library/Fonts/Supplemental/Arial.ttf"
        sys_b = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        sys_i = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"
        sys_bi = "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf"
        if os.path.exists(sys_r) and os.path.exists(sys_b):
            r_path, b_path, i_path, bi_path = sys_r, sys_b, sys_i, sys_bi

    if os.path.exists(r_path) and os.path.exists(b_path):
        pdfmetrics.registerFont(TTFont("AppFont", r_path))
        pdfmetrics.registerFont(TTFont("AppFont-Bold", b_path))
        pdfmetrics.registerFont(TTFont("AppFont-Italic", i_path if os.path.exists(i_path) else r_path))
        pdfmetrics.registerFont(TTFont("AppFont-BoldItalic", bi_path if os.path.exists(bi_path) else b_path))

        addMapping("AppFont", 0, 0, "AppFont")
        addMapping("AppFont", 1, 0, "AppFont-Bold")
        addMapping("AppFont", 0, 1, "AppFont-Italic")
        addMapping("AppFont", 1, 1, "AppFont-BoldItalic")
        registerFontFamily("AppFont", normal="AppFont", bold="AppFont-Bold", italic="AppFont-Italic", boldItalic="AppFont-BoldItalic")
        return "AppFont", "AppFont-Bold", "AppFont-Italic"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"

FONT_REGULAR, FONT_BOLD, FONT_ITALIC = register_custom_fonts()

class NumberedCanvas(canvas.Canvas):
    """Kétoldalas canvas oldalszámozással és elegáns lábléccel"""
    def __init__(self, *args, **kwargs):
        self.footer_lang = kwargs.pop('footer_lang', 'en')
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont(FONT_REGULAR, 8)
        self.setFillColor(colors.HexColor("#71717a"))
        
        self.setStrokeColor(colors.HexColor("#e4e4e7"))
        self.setLineWidth(0.5)
        self.line(36, 30, A4[0] - 36, 30)
        
        if getattr(self, 'footer_lang', 'en') == 'hu':
            left_text = "Eszes Richárd — Önéletrajz | richard@eszes.me | https://eszes.me"
            page_text = f"{self._pageNumber}. oldal / {page_count}"
        else:
            left_text = "Richárd Eszes — Curriculum Vitae | richard@eszes.me | https://eszes.me"
            page_text = f"Page {self._pageNumber} of {page_count}"
        
        self.drawString(36, 20, left_text)
        self.drawRightString(A4[0] - 36, 20, page_text)
        self.restoreState()

def create_circular_avatar(input_path, output_path, size=(240, 240)):
    """Kör alakú profilfotó előállítása finom szegéllyel"""
    img = PILImage.open(input_path).convert("RGB")
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    img_cropped = img.crop((left, top, left + min_dim, top + min_dim))
    img_resized = img_cropped.resize(size, PILImage.Resampling.LANCZOS)
    
    mask = PILImage.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    
    output = PILImage.new('RGBA', size, (255, 255, 255, 0))
    output.paste(img_resized, (0, 0), mask=mask)
    output.save(output_path, "PNG")

def generate_cv_for_lang(lang="en"):
    os.makedirs("assets/cv", exist_ok=True)
    os.makedirs("assets/images", exist_ok=True)
    
    filename = f"Richard_Eszes_Software_Developer_CV_{lang.upper()}.pdf"
    pdf_path = os.path.join("assets/cv", filename)
    avatar_path = "assets/images/avatar_circle.png"

    if os.path.exists("assets/images/profile.jpg") and not os.path.exists(avatar_path):
        create_circular_avatar("assets/images/profile.jpg", avatar_path, size=(220, 220))

    # A4: 595.27 x 841.89 pt. 36 pt (~12.7 mm) margó
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=32,
        bottomMargin=38
    )

    printable_width = A4[0] - 72

    c_primary = colors.HexColor("#09090b")
    c_secondary = colors.HexColor("#27272a")
    c_muted = colors.HexColor("#52525b")
    c_border = colors.HexColor("#e4e4e7")
    c_blue = colors.HexColor("#2563eb")

    name_style = ParagraphStyle(
        'CVName',
        fontName=FONT_BOLD,
        fontSize=20,
        leading=23,
        textColor=c_primary,
    )

    title_style = ParagraphStyle(
        'CVTitle',
        fontName=FONT_BOLD,
        fontSize=10,
        leading=13,
        textColor=c_blue,
    )

    contact_style = ParagraphStyle(
        'CVContact',
        fontName=FONT_REGULAR,
        fontSize=8.2,
        leading=11.5,
        textColor=c_muted,
    )

    section_header_style = ParagraphStyle(
        'CVSectionHeader',
        fontName=FONT_BOLD,
        fontSize=9.5,
        leading=12,
        textColor=c_primary,
        spaceBefore=0,
        spaceAfter=3,
        textTransform='uppercase',
    )

    body_style = ParagraphStyle(
        'CVBody',
        fontName=FONT_REGULAR,
        fontSize=8.3,
        leading=11.8,
        textColor=c_secondary,
    )

    body_bold = ParagraphStyle(
        'CVBodyBold',
        fontName=FONT_BOLD,
        fontSize=8.3,
        leading=11.8,
        textColor=c_primary,
    )

    job_title_style = ParagraphStyle(
        'CVJobTitle',
        fontName=FONT_BOLD,
        fontSize=9.2,
        leading=12,
        textColor=c_primary,
    )

    job_meta_style = ParagraphStyle(
        'CVJobMeta',
        fontName=FONT_REGULAR,
        fontSize=8.2,
        leading=11,
        textColor=c_muted,
        alignment=2,
    )

    bullet_style = ParagraphStyle(
        'CVBullet',
        fontName=FONT_REGULAR,
        fontSize=8.1,
        leading=11.2,
        textColor=c_secondary,
        leftIndent=10,
        firstLineIndent=-10,
        spaceAfter=2,
    )

    tech_line_style = ParagraphStyle(
        'CVTechLine',
        fontName=FONT_ITALIC,
        fontSize=7.8,
        leading=10.5,
        textColor=c_muted,
    )

    def make_section_divider(title_text):
        return [
            Paragraph(title_text, section_header_style),
            HRFlowable(width="100%", thickness=0.75, color=c_border, spaceBefore=2, spaceAfter=5)
        ]

    story = []

    # =========================================================================
    # TARTALMI ELEMEK NYELVTŐL FÜGGŐEN
    # =========================================================================
    if lang == "hu":
        header_name = "ESZES RICHÁRD"
        header_title = "Senior Szoftverfejlesztő &bull; Backend Rendszerarchitektúra"
        header_contact = (
            "<b>E-mail:</b> richard@eszes.me &nbsp;|&nbsp; <b>Telefon:</b> +36 30 533 9792 &nbsp;|&nbsp; <b>Lokáció:</b> Pécs, Magyarország<br/>"
            "<b>LinkedIn:</b> linkedin.com/in/richardeszes &nbsp;|&nbsp; <b>Portfólió:</b> https://eszes.me"
        )
        sec_summary = "Szakmai Összefoglaló"
        summary_text = (
            "<b>Több mint 10 év szakmai tapasztalattal rendelkező szoftverfejlesztő</b>, robusztus backend rendszerek, "
            "ipari gyártásirányítási megoldások (MES) és nagy rendelkezésre állású vállalati webes platformok tervezésére és fejlesztésére specializálódva (PHP, Laravel, Yii2, MySQL, PostgreSQL). "
            "Kiemelt tapasztalat a <b>Domain-Driven Design (DDD)</b> és a SOLID elvek gyakorlati alkalmazásában, automatizált tesztelésben (PHPUnit, Cypress), "
            "valamint szigorú gyógyszeripari szabályozási előírásoknak (GMP) és elektronikus audit traileknek megfelelő rendszerek szállításában. "
            "A mérnöki precizitást üzleti szemlélettel ötvözi, jelenleg a Pécsi Tudományegyetem <b>Gazdálkodási és menedzsment alapképzésének (BSc)</b> hallgatója."
        )
        sec_skills = "Készségek &amp; Technológiai Verem"
        skills_data = [
            [Paragraph("<b>Backend &amp; Architektúra:</b>", body_bold),
             Paragraph("PHP 8+, Laravel, Domain-Driven Design (DDD), Yii2, RESTful API tervezés, SOLID elvek, Active Directory hitelesítés", body_style)],
            [Paragraph("<b>Adatbázisok &amp; DevOps:</b>", body_bold),
             Paragraph("MySQL, PostgreSQL, Adatbázis-normalizálás &amp; optimalizálás, Migrációk, Docker, Git, GitLab CI/CD, Linux", body_style)],
            [Paragraph("<b>AI &amp; Fejlesztési Eszközök:</b>", body_bold),
             Paragraph("AI Coding Agents (Antigravity, Cursor, Copilot), Spec-Driven Development (SDD), GitHub Spec-Kit, Prompt Engineering", body_style)],
            [Paragraph("<b>Tesztelés &amp; Minőség:</b>", body_bold),
             Paragraph("PHPUnit (Unit tesztek), Cypress (E2E tesztek), Agilis szoftverfejlesztés / Scrum, Kódellenőrzés, GMP előírások", body_style)],
            [Paragraph("<b>Frontend &amp; CMS:</b>", body_bold),
             Paragraph("JavaScript (ES6+), HTML5, CSS3, SASS / SCSS, Bootstrap, Ionic Framework, WordPress Core &amp; Egyedi bővítmények", body_style)],
            [Paragraph("<b>Üzlet &amp; Menedzsment:</b>", body_bold),
             Paragraph("Vállalati pénzügyek, Folyamatmenedzsment, Projektmenedzsment, Üzleti kommunikáció, HR menedzsment", body_style)],
        ]
        sec_experience = "Szakmai Tapasztalat"
        p1_title = "Software Developer &mdash; <b>Contrall Ipari Informatikai Kft.</b>"
        p1_meta = "2022. 01 &ndash; Jelenleg | Pécs, Magyarország"
        p1_bullets = [
            "&bull; <b>Ipari MES fejlesztés:</b> Yii2 alapú gyártásirányítási rendszer (MES) fejlesztése és karbantartása gép- és fémipari KKV partnerek számára; valós idejű termeléskövetés, operátori terminálok, gép-ciklusidő elemzés és gyári beléptetés.",
            "&bull; <b>Gyógyszerbiztonsági minőségbiztosítási rendszer:</b> Egyedi Laravel platform szállítása vezető gyógyszergyár számára szigorú <b>GMP/GxP előírások</b> betartásával, manipulációbiztos elektronikus audit trailekkel és Active Directory autentikációval.",
            "&bull; <b>Automatizált tesztelés &amp; CI/CD:</b> Teljeskörű automatizált tesztlefedettség kialakítása <b>PHPUnit</b> és <b>Cypress</b> technológiákkal; konténerizált élesítési folyamatok Docker és GitLab CI rendszerekben.",
            "&bull; <b>Adatbázis-architektúra:</b> Relációs adatbázis-sémák tervezése és optimalizálása MySQL és PostgreSQL környezetben, szigorú normalizálás és index-tuning.",
            "Technológiák: Yii2, Laravel, PHP 8+, MySQL, PostgreSQL, Docker, Cypress, PHPUnit, Active Directory, GitLab CI"
        ]
        p2_title = "PHP Developer &mdash; <b>Arteries Studio Kft.</b>"
        p2_meta = "2013 &ndash; 2021. 12 (~9 év) | Pécs, Magyarország"
        p2_bullets = [
            "&bull; <b>Vállalati webes média:</b> Egyedi, nagy látogatottságra optimalizált WordPress sablon- és bővítményarchitektúra fejlesztése egy világvezető <b>Big Four tanácsadó cég</b> magyarországi szakmai blogja és tudástára számára.",
            "&bull; <b>Egyedi platform- &amp; API fejlesztés:</b> Skálázható backend rendszerek fejlesztése Laravel és saját MVC motorokon landing page-ekhez, e-kereskedelmi portálokhoz és mobil alkalmazások RESTful API-jaihoz.",
            "&bull; <b>Rendszerintegrációk:</b> Harmadik féltől származó ERP, CRM, fizetési és számlázó API-k összekapcsolása több tucat hazai KKV számára, automatizálva a számlázást és raktárkészlet-szinkront.",
            "&bull; <b>Full-stack megvalósítás:</b> Reszponzív felületek szállítása JavaScript (ES6+), SASS/SCSS és HTML5 technológiákkal asztali és mobil eszközökre.",
            "Technológiák: PHP, Laravel, WordPress, MySQL, REST API, JavaScript, SASS, Bootstrap, Git"
        ]
        sec_projects = "Kiemelt Szakmai Projektek"
        projects = [
            ("Új Generációs Gyártásirányítási Rendszer (MES 2.0)", "Laravel, DDD, PostgreSQL, Docker, REST API, Egyedi Sablon",
             "A gyártásirányítási platform modern, Domain-Driven Design (DDD) alapú újraírása. Raktározás és készletkezelés, valós idejű gyártáskövetés, értékesítésmenedzsment, REST API és egyedi sablonarchitektúra."),
            ("Gyógyszerbiztonsági Minőségbiztosítási Rendszer", "Laravel, PostgreSQL, Active Directory, Audit Trail, Docker",
             "Kritikus belső minőségbiztosítási és folyamatvalidáló platform gyógyszergyár számára. Teljes GMP/GxP megfelelőség manipulációbiztos audit naplókkal és AD jogosultságkezeléssel."),
            ("Internetszolgáltató CRM &amp; Ügyfélkapu Rendszer", "Laravel, Bootstrap, Docker, MySQL, REST API, Műholdas API Integráció",
             "Telekommunikációs szolgáltató komplex CRM és ügyfélkapu rendszere. Lead-ek kezelése, automatizált szerződésgenerálás és külső műholdas szolgáltató REST API integrációja előfizetések valós idejű kezelésére."),
            ("Gyártásirányítási Rendszer (MES)", "Yii2, PHP, MySQL, Cypress, Bootstrap, PHPUnit",
             "Ipari termeléskövetés, gép-ciklusidő elemzés, operátori terminálok, értékesítés és gyári beléptető rendszer gép- és fémipari KKV partnerek számára."),
            ("Big Four Tanácsadó Cég &mdash; Szakmai Blog", "WordPress, PHP, SASS, JavaScript",
             "Egyedi sablon- és bővítményarchitektúra egy globális Big Four tanácsadó cég hivatalos tudásbázisához és szakmai blogjához, nagy forgalomra méretezve."),
            ("Egyedi KKV Rendszerek &amp; Webáruházak", "PHP, Egyedi MVC, Laravel, MySQL, REST API",
             "Több tucat egyedi webes alkalmazás, B2B/B2C webáruház és külső ERP/számlázó API szinkronizáció hazai kis- és középvállalkozások digitalizálására."),
        ]
        sec_education = "Tanulmányok &amp; Képzettség"
        edu_items = [
            ("Gazdálkodási és menedzsment alapszak (BSc)", "2026 &ndash; Jelenleg (Folyamatban)",
             "Pécsi Tudományegyetem, Közgazdaságtudományi Kar (PTE KTK)",
             "Felsőfokú egyetemi alapképzés. Stratégiai menedzsment, vállalati pénzügyek, kontrolling és döntéstámogató rendszerek. ISCED level 6 &bull; EQF level 6"),
            ("Business Administration Assistant", "2021 &ndash; 2023",
             "Pécsi Tudományegyetem, Közgazdaságtudományi Kar (PTE KTK)",
             "4 féléves felsőoktatási szakképzés (FOSZK). Vállalati gazdaságtan, pénzügyi alapok és üzleti adminisztráció. ISCED level 5 &bull; EQF level 5"),
            ("Webfejlesztő", "2011 &ndash; 2013",
             "Lia Alapítványi Szakközépiskola, Budapest",
             "4 féléves érettségi utáni szakképzés. Relációs adatbázis-kezelés, webes szabványok, kliens- és szerveroldali programozás. ISCED level 4 &bull; EQF level 4/5"),
        ]
        sec_extras = "További Képzés, Nyelvtudás &amp; Érdeklődés"
        extras_data = [
            [Paragraph("<b>Képzés:</b>", body_bold),
             Paragraph("<b>Digital Finance Training (2022)</b> &mdash; Pécsi Tudományegyetem, Közgazdaságtudományi Kar (PTE KTK)", body_style)],
            [Paragraph("<b>Nyelvtudás:</b>", body_bold),
             Paragraph("<b>Magyar:</b> Anyanyelv &nbsp;|&nbsp; <b>Angol:</b> B2 felső-középfok (Euroexam, 2025)", body_style)],
            [Paragraph("<b>Érdeklődés:</b>", body_bold),
             Paragraph("Technológiai trendek &amp; digitális eszközök, Személyes pénzügyek &amp; közgazdaságtan, Asztronómia, Pszichológia, Külpolitika, Fotózás", body_style)]
        ]
    else:
        # ANGOL VERZIÓ
        header_name = "RICHÁRD ESZES"
        header_title = "Senior Software Developer &bull; Backend Architecture"
        header_contact = (
            "<b>Email:</b> richard@eszes.me &nbsp;|&nbsp; <b>Phone:</b> +36 30 533 9792 &nbsp;|&nbsp; <b>Location:</b> Pécs, Hungary<br/>"
            "<b>LinkedIn:</b> linkedin.com/in/richardeszes &nbsp;|&nbsp; <b>Portfolio:</b> https://eszes.me"
        )
        sec_summary = "Professional Summary"
        summary_text = (
            "<b>Senior software developer with over 10 years of professional experience</b> specializing in robust backend architectures, "
            "industrial Manufacturing Execution Systems (MES), and high-availability web platforms (PHP, Laravel, Yii2, MySQL, PostgreSQL). "
            "Extensive background delivering mission-critical applications under strict regulatory compliance, including pharmaceutical QA systems "
            "aligned with GMP/GxP standards and tamper-evident audit trails. Strong advocate of <b>Domain-Driven Design (DDD)</b>, SOLID principles, "
            "and automated testing (PHPUnit, Cypress). Combines deep engineering capability with strategic business acumen, currently pursuing a "
            "<b>BSc in Business Administration and Management</b> at the University of Pécs."
        )
        sec_skills = "Skills &amp; Technology Stack"
        skills_data = [
            [Paragraph("<b>Backend &amp; Architecture:</b>", body_bold),
             Paragraph("PHP 8+, Laravel, Domain-Driven Design (DDD), Yii2, RESTful API Design, SOLID Principles, Active Directory Auth", body_style)],
            [Paragraph("<b>Databases &amp; DevOps:</b>", body_bold),
             Paragraph("MySQL, PostgreSQL, Database Normalization &amp; Optimization, Migrations, Docker, Git, GitLab CI/CD, Linux", body_style)],
            [Paragraph("<b>AI &amp; Developer Tooling:</b>", body_bold),
             Paragraph("AI Coding Agents (Antigravity, Cursor, Copilot), Spec-Driven Development (SDD), GitHub Spec-Kit, Prompt Engineering", body_style)],
            [Paragraph("<b>Testing &amp; Quality:</b>", body_bold),
             Paragraph("PHPUnit (Unit Testing), Cypress (E2E Testing), Agile / Scrum, Code Reviews, Regulatory Compliance (GMP / GxP)", body_style)],
            [Paragraph("<b>Frontend &amp; CMS:</b>", body_bold),
             Paragraph("JavaScript (ES6+), HTML5, CSS3, SASS / SCSS, Bootstrap, Ionic Framework, WordPress Core &amp; Custom Plugins", body_style)],
            [Paragraph("<b>Business &amp; Management:</b>", body_bold),
             Paragraph("Corporate Finance, Process Management, Project Leadership, Business Communication, HR Management", body_style)],
        ]
        sec_experience = "Work Experience"
        p1_title = "Software Developer &mdash; <b>Contrall Ipari Informatikai Kft.</b>"
        p1_meta = "Jan 2022 &ndash; Present | Pécs, Hungary"
        p1_bullets = [
            "&bull; <b>Industrial MES Engineering:</b> Develop and maintain a Yii2-based Manufacturing Execution System (MES) helping machinery and metalworking SMEs digitize job tracking, machine cycle times, operator workflows, and facility access control.",
            "&bull; <b>Pharma QA &amp; Compliance System:</b> Engineered an internal quality assurance platform for a pharmaceutical plant adhering to strict <b>GMP/GxP standards</b>, implementing tamper-evident electronic audit trails and Active Directory authentication.",
            "&bull; <b>Automated Testing &amp; CI/CD:</b> Established test coverage using <b>PHPUnit</b> and <b>Cypress</b> (E2E workflows); streamlined deployments using Docker containerization and GitLab CI pipelines.",
            "&bull; <b>Database Architecture:</b> Designed and optimized relational schemas in MySQL and PostgreSQL, enforcing strict normalization, data integrity, and index tuning.",
            "Technologies: Yii2, Laravel, PHP 8+, MySQL, PostgreSQL, Docker, Cypress, PHPUnit, Active Directory, GitLab CI"
        ]
        p2_title = "PHP Developer &mdash; <b>Arteries Studio Kft.</b>"
        p2_meta = "2013 &ndash; Dec 2021 (~9 yrs) | Pécs, Hungary"
        p2_bullets = [
            "&bull; <b>Enterprise Web Publishing:</b> Engineered a bespoke, lightweight WordPress theme and tailored plugin architecture for the Hungarian thought-leadership blog and knowledge repository of a global <b>Big Four advisory firm</b>.",
            "&bull; <b>Custom Web &amp; API Development:</b> Architected backend systems on Laravel and bespoke PHP MVC engines for client webshops, high-converting landing pages, and RESTful APIs serving mobile applications.",
            "&bull; <b>Third-Party Integrations:</b> Integrated external ERP, CRM, payment gateway, and billing APIs for dozens of domestic SME clients, automating invoice generation and inventory synchronization.",
            "&bull; <b>Full-Stack Delivery:</b> Implemented responsive frontend interfaces using JavaScript (ES6+), SASS/SCSS, and HTML5 across desktop and mobile devices.",
            "Technologies: PHP, Laravel, WordPress, MySQL, REST APIs, JavaScript, SASS, Bootstrap, Git"
        ]
        sec_projects = "Selected Key Projects &amp; Deliverables"
        projects = [
            ("Next-Gen Manufacturing Execution System (MES 2.0)", "Laravel, DDD, PostgreSQL, Docker, REST API, Bespoke UI",
             "Modern re-architecture of the manufacturing execution platform using Domain-Driven Design (DDD) principles. Comprehensive warehousing, real-time production tracking, sales lifecycle, and REST APIs."),
            ("Pharmaceutical QA &amp; Compliance System", "Laravel, PostgreSQL, Active Directory, Audit Trail, Docker",
             "Mission-critical internal QA and workflow validation platform for a pharmaceutical manufacturing plant. Compliant with strict GMP/GxP standards with tamper-evident audit logs and AD role management."),
            ("ISP CRM &amp; Customer Portal System", "Laravel, Bootstrap, Docker, MySQL, REST API, Satellite API",
             "End-to-end CRM and customer self-service portal for an Internet Service Provider. Lead pipeline tracking, automated contract generation, and REST API integration with an external satellite provider for live provisioning."),
            ("Manufacturing Execution System (MES)", "Yii2, PHP, MySQL, Cypress, Bootstrap, PHPUnit",
             "Industrial production tracking, machine cycle time metrics, operator terminal interfaces, sales workflows, and facility access control tailored for machinery and metalworking SME partners."),
            ("Big Four Advisory Firm &mdash; Professional Blog", "WordPress, PHP, SASS, JavaScript",
             "Bespoke theme and plugin architecture engineered for the official knowledge base and business blog of a global Big Four advisory firm, optimized for editorial agility and high traffic."),
            ("Custom SME Platforms &amp; E-Commerce Webshops", "PHP, Custom MVC, Laravel, MySQL, REST API",
             "Dozens of custom web applications, B2B/B2C online stores, and third-party ERP/billing API synchronizations delivered to automate business operations for domestic SMEs."),
        ]
        sec_education = "Education &amp; Academic Background"
        edu_items = [
            ("BSc in Business Administration and Management", "2026 &ndash; Present (In Progress)",
             "University of Pécs, Faculty of Business and Economics (PTE KTK)",
             "Undergraduate university degree program. Strategic management, corporate finance, controlling, and decision-support systems. ISCED level 6 &bull; EQF level 6"),
            ("Business Administration Assistant", "2021 &ndash; 2023",
             "University of Pécs, Faculty of Business and Economics (PTE KTK)",
             "4-semester higher vocational training (FOSZK). Corporate economics, financial management, and business administration. ISCED level 5 &bull; EQF level 5"),
            ("Web Developer", "2011 &ndash; 2013",
             "Lia Foundation Vocational School, Budapest",
             "4-semester post-secondary vocational qualification. Relational database management, web standards, client- and server-side software development. ISCED level 4 &bull; EQF level 4/5"),
        ]
        sec_extras = "Additional Training, Languages &amp; Interests"
        extras_data = [
            [Paragraph("<b>Training:</b>", body_bold),
             Paragraph("<b>Digital Finance Training (2022)</b> &mdash; University of Pécs, Faculty of Business and Economics (PTE KTK)", body_style)],
            [Paragraph("<b>Languages:</b>", body_bold),
             Paragraph("<b>Hungarian:</b> Native &nbsp;|&nbsp; <b>English:</b> Upper-Intermediate B2 (Euroexam, 2025)", body_style)],
            [Paragraph("<b>Interests:</b>", body_bold),
             Paragraph("Technology trends &amp; digital tools, Personal finance &amp; economics, Astronomy, Psychology, Foreign affairs, Photography", body_style)]
        ]

    # =========================================================================
    # PAGE 1 FELÉPÍTÉSE
    # =========================================================================
    left_info = [
        Paragraph(header_name, name_style),
        Paragraph(header_title, title_style),
        Spacer(1, 3),
        Paragraph(header_contact, contact_style)
    ]

    if os.path.exists(avatar_path):
        avatar_img = Image(avatar_path, width=60, height=60)
        header_table = Table([[left_info, avatar_img]], colWidths=[printable_width - 68, 68])
    else:
        header_table = Table([[left_info]], colWidths=[printable_width])

    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=7))

    # Summary
    story.extend(make_section_divider(sec_summary))
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 6))

    # Skills Matrix
    story.extend(make_section_divider(sec_skills))
    col_w1 = 130 if lang == "hu" else 126
    skills_table = Table(skills_data, colWidths=[col_w1, printable_width - col_w1])
    skills_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 6))

    # Work Experience
    story.extend(make_section_divider(sec_experience))

    # Pos 1
    p1_head = Table([
        [Paragraph(p1_title, job_title_style),
         Paragraph(p1_meta, job_meta_style)]
    ], colWidths=[printable_width - 150, 150])
    p1_head.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BASELINE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ]))
    story.append(p1_head)
    for b in p1_bullets[:-1]:
        story.append(Paragraph(b, bullet_style))
    story.append(Paragraph(p1_bullets[-1], tech_line_style))
    story.append(Spacer(1, 6))

    # Pos 2
    p2_head = Table([
        [Paragraph(p2_title, job_title_style),
         Paragraph(p2_meta, job_meta_style)]
    ], colWidths=[printable_width - 150, 150])
    p2_head.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BASELINE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ]))
    story.append(p2_head)
    for b in p2_bullets[:-1]:
        story.append(Paragraph(b, bullet_style))
    story.append(Paragraph(p2_bullets[-1], tech_line_style))

    # OLDALTÖRÉS A 2. OLDALRA
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2 FELÉPÍTÉSE
    # =========================================================================
    story.extend(make_section_divider(sec_projects))
    for p_title, p_tech, p_desc in projects:
        story.append(Paragraph(f"<b>{p_title}</b> &nbsp;|&nbsp; <font color='#52525b'>{p_tech}</font>", body_bold))
        story.append(Paragraph(p_desc, bullet_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 6))

    # Education
    story.extend(make_section_divider(sec_education))
    for degree, dates, school, desc in edu_items:
        edu_row = Table([
            [Paragraph(f"<b>{degree}</b> &mdash; {school}", body_style),
             Paragraph(dates, job_meta_style)]
        ], colWidths=[printable_width - 140, 140])
        edu_row.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BASELINE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ]))
        story.append(edu_row)
        story.append(Paragraph(desc, bullet_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 6))

    # Extras
    story.extend(make_section_divider(sec_extras))
    col_w_extra = 76 if lang == "hu" else 76
    extras_table = Table(extras_data, colWidths=[col_w_extra, printable_width - col_w_extra])
    extras_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(extras_table)

    # Canvas készítő testreszabása az adott nyelvvel
    class CustomCanvas(NumberedCanvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, footer_lang=lang, **kwargs)

    doc.build(story, canvasmaker=CustomCanvas)
    print(f"CV ({lang.upper()}) successfully generated at: {pdf_path}")

def generate_all():
    generate_cv_for_lang("en")
    generate_cv_for_lang("hu")

if __name__ == "__main__":
    generate_all()
