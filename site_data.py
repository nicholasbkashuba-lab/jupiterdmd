"""Every fact, page and line of copy on jupiterdmd.com.

build.py renders this file; nothing in it is invented. Where a fact comes from
somewhere other than the practice's own website, the source is named next to it.
Anything marked CONFIRM is held back from the page until the practice confirms it.
"""

# --- The practice -----------------------------------------------------------
# Sources: the practice's own site (Officite, captured by Common Crawl July 2024),
# the NPPES NPI registry (NPI 1013119932, fetched 2026-10-19) and Healthgrades.

PRACTICE = {
    "name": "Angelo Forte, DMD",                 # public name used on the old site and in GBP-style listings
    "legal_name": "Angelo Forte, D.M.D., P.A.",  # NPI location record: "ANGELO FORTE,D.M.D,P.A"
    "descriptor": "General & Cosmetic Dentistry",
    "doctor": "Dr. Angelo Forte",
    "doctor_full": "Angelo G. Forte, DMD",       # middle name Gabriele per NPI
    "street": "654 W. Indiantown Rd., Suite 105",
    "street_schema": "654 W Indiantown Rd, Suite 105",
    "city": "Jupiter",
    "region": "FL",
    "zip": "33458",
    "phone": "(561) 747-2134",
    "phone_e164": "+15617472134",
    "fax": "(561) 747-2122",                     # NPI registry + Healthgrades
    "lat": 26.9340672,                           # OpenStreetMap geocode of the street address
    "lng": -80.1049793,
    "npi": "1013119932",
    "license": "DN14440",                        # Florida dental license, NPI taxonomy record
    "maps_url": "https://www.google.com/maps/search/?api=1&query=Angelo+Forte+DMD+654+W+Indiantown+Rd+Suite+105+Jupiter+FL+33458",
    "license_verify_url": "https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders",
    "npi_url": "https://npiregistry.cms.hhs.gov/provider-view/1013119932",
    "healthgrades_url": "https://www.healthgrades.com/dentist/dr-angelo-forte-2swxs",
    "carecredit_url": "https://www.carecredit.com/doctor-locator/jupiter-fl/angelo-forte-dmd-llc-dvb794/",
}

# Hours as published on the practice's own site (July 2024). CONFIRM before launch:
# the old site's schema contradicted its own page (it said Friday 9-5 and "Fr 0:00").
HOURS = [
    ("Monday", "Mo", "08:00", "17:00"),
    ("Tuesday", "Tu", "08:00", "17:00"),
    ("Wednesday", "We", "08:00", "17:00"),
    ("Thursday", "Th", "08:00", "17:00"),
]
HOURS_NOTES = [
    "Closed for lunch 1:00 to 2:00 PM, Monday to Thursday",
    "Friday by appointment only",
    "Saturday and Sunday closed",
]

# Held back until the practice confirms (listed by Healthgrades, not by the practice).
CONFIRM_LANGUAGES = ["English", "Italian", "Spanish"]
CONFIRM_EDUCATION = "University of Florida"

# Measured drive times from the office (OSRM routing over OpenStreetMap, free-flow;
# real traffic runs longer, so copy says "about" and "outside rush hour").
NEARBY = [
    ("Harbourside Place", 1.7, 3),
    ("Jupiter Medical Center", 1.4, 4),
    ("Jupiter Community High School", 1.2, 4),
    ("Carlin Park", 2.8, 6),
    ("Jupiter Inlet Lighthouse", 3.0, 7),
]

# --- Testimonials ------------------------------------------------------------
# Verbatim from the practice's own /testimonials page (captured July 2024),
# attributed exactly as the practice published them. Never edit the wording.
TESTIMONIALS = [
    ("Top Notch! Dr. Forte & his amazing staff of professionals went above & beyond to treat me like a valued customer. It feels good to know people still care & have passion in their craft. My entire Family looks forward to going to Dr. Forte’s office for a fun & pleasant experience! A-Plus!", "Conor Alexander"),
    ("Dr. Forte is wonderful, he is kind, caring and he knows his stuff. He treated me with exceptional care & I fully trust his decisions 100%. He truly cares about his patients and does what is best for the patient. I recommend Dr. Forte to everyone in need of a dentist and would never go anywhere else.", "Anonymous"),
    ("Dr Forte and his staff operate the best dental office i have ever had the good fortune to use. Dr Forte's ability is outstanding offering fast and easy care to patients. He is assisted by a highly qualified staff. I highly recommend him for your dental needs.", "Bucky Buchwald"),
    ("Just amazing experience, Haven't been to the dentist in a really long time and was amazed by the treatment and care I received also at so much below what I've ever paid before. Dr. Forte is awesome.", "Jenny C"),
    ("Would recommend this dentist in a heartbeat, seriously you will not find better he is so caring and truly knows his stuff. He is a great dentist and person.", "Self-verified patient of Dr. Angelo G Forte"),
    ("Just a wonderful guy. He is smart and caring. Staff is lovely, too. Going to the dentist can be pleasureable !", "Re"),
    ("THE BEST DENTIST EVER, TOTALLY DEDICATED TO HIS PATIENT. STAFF IS JUST SUPER.", "Anonymous"),
    ("Dr. Forte is a wonderful dentist who really cares about his patients.", "Jojo Yogi"),
    ("Dr. Forte is \"The Best\"!!!!", "Harmony AH"),
]

# --- Services ----------------------------------------------------------------
# The list is the practice's own (old /dental-services page, plus Invisalign and
# digital X-rays from its "Facilities and Equipment" list). The explanatory copy is
# general patient education written for this site: no outcome promises, no prices,
# no claim about who performs which step. Dr. Forte should read it before launch.

GROUPS = [
    ("preventive", "Keep it healthy", "Preventive care"),
    ("restorative", "Fix what's wrong", "Restorative care"),
    ("cosmetic", "Change how it looks", "Cosmetic dentistry"),
    ("replace", "Replace what's missing", "Tooth replacement"),
    ("relief", "Stop the pain", "Pain & urgent care"),
]

SERVICES = [
    {
        "slug": "exams-cleanings",
        "group": "preventive",
        "name": "Exams & Cleanings",
        "nav": "Exams & cleanings",
        "title": "Dental Exams & Cleanings in Jupiter, FL | Angelo Forte, DMD",
        "desc": "Professional cleanings, dental exams, oral cancer screenings, sealants and digital X-rays at Angelo Forte, DMD on W. Indiantown Rd. in Jupiter. Call (561) 747-2134.",
        "h1_lead": "Dental exams & cleanings in Jupiter",
        "h1": "The visit that keeps the others small.",
        "lede": "A cleaning and exam is where most problems get caught while they are still cheap and simple to fix. It is also where we get to know your mouth, so changes stand out.",
        "short": "Cleanings, exams, oral cancer screenings, sealants and digital X-rays.",
        "specialty": "Dentistry",
        "about": ["Dental caries", "Periodontal disease", "Oral cancer"],
        "sections": [
            ("What happens at a check-up", """
<p>Your hygienist removes the plaque and hardened tartar that brushing and flossing leave behind, especially along and just under the gumline, then polishes the teeth. Dr. Forte examines your teeth, gums, bite and the soft tissue of your mouth, and reviews X-rays when they are due.</p>
<p>The practice uses <strong>digital X-rays</strong>. They show decay between teeth, bone levels and problems below the gumline that an eye can't see, and the images are ready on screen straight away so you can look at them together.</p>"""),
            ("Oral cancer screening", """
<p>Oral cancer screening is part of the exam. Dr. Forte looks and feels for sores, patches, lumps or color changes on the tongue, cheeks, floor of the mouth, palate and throat. It takes a minute and is painless. Anything that looks unusual is watched or referred for a closer look, because early findings are far easier to treat.</p>"""),
            ("Sealants for children", """
<p>The back teeth have deep grooves that a toothbrush struggles to reach. A sealant is a thin protective coating painted into those grooves to keep food and bacteria out. It is quick, involves no drilling and is most often placed on children's permanent molars soon after they come in.</p>"""),
            ("How often should you come in?", """
<p>Many patients do well with a cleaning and exam every six months. Some need to come more often, for example people with a history of gum disease, frequent cavities or certain medical conditions. Dr. Forte will tell you what interval makes sense for you and why.</p>"""),
        ],
        "faqs": [
            ("How often do I need a dental cleaning?", "Many patients come every six months. If you have a history of gum disease or frequent cavities, Dr. Forte may suggest a shorter interval. He will explain the reason for whatever schedule he recommends."),
            ("Do you use digital X-rays?", "Yes. The practice lists digital X-rays among its equipment. Images appear on screen straight away so Dr. Forte can show you what he is seeing."),
            ("Is an oral cancer screening included in my exam?", "Oral cancer screening is part of the practice's preventive care. It is a quick visual and hands-on check of the tissues in your mouth and throat."),
        ],
        "related": ["fillings", "gum-disease-treatment", "teeth-whitening"],
    },
    {
        "slug": "fillings",
        "group": "restorative",
        "name": "Fillings",
        "nav": "Fillings",
        "title": "Tooth-Colored Fillings in Jupiter, FL | Angelo Forte, DMD",
        "desc": "Cavity treatment and replacement of old fillings at Angelo Forte, DMD in Jupiter, FL. Find out what a filling involves and how to tell if you need one. (561) 747-2134.",
        "h1_lead": "Dental fillings in Jupiter",
        "h1": "Small cavity, small repair.",
        "lede": "A filling removes decay and rebuilds the tooth so it is strong and comfortable to chew on again. Caught early, a cavity usually needs nothing more.",
        "short": "Repair cavities and replace old, worn or broken fillings.",
        "specialty": "Dentistry",
        "about": ["Dental caries"],
        "sections": [
            ("Signs you may need a filling", """
<p>Early decay often has no symptoms at all, which is why it is usually found at a check-up or on an X-ray. As it grows you may notice sensitivity to sweets, hot or cold, a rough edge your tongue keeps finding, food catching between two teeth, or a dark spot. An old filling that has cracked, leaks or has decay around its edge also needs attention.</p>"""),
            ("What happens at the appointment", """
<p>The tooth is numbed, the decayed part is removed and the space is cleaned. The filling material is then placed, shaped to fit your bite and polished. Most fillings are done in a single visit. Your lip and tongue may stay numb for a couple of hours, so take care eating until the feeling returns.</p>"""),
            ("Choosing a filling material", """
<p>Fillings can be made from several materials, including tooth-colored composite resin and silver amalgam. Each has trade-offs in strength, appearance and cost. Dr. Forte will explain which suits the size and position of your cavity, and answer questions about any material, including the safety of amalgam, before you decide.</p>"""),
        ],
        "faqs": [
            ("Does getting a filling hurt?", "The tooth is numbed before any work begins, so most people feel pressure rather than pain. Some sensitivity for a few days afterwards is common and usually settles on its own. Call the office if it doesn't."),
            ("Can old silver fillings be replaced?", "Yes. Old fillings that are worn, cracked or leaking can be replaced. Dr. Forte will tell you whether a filling actually needs replacing or is still doing its job."),
            ("How long does a filling take?", "Most fillings are finished in one appointment. Larger or multiple fillings take longer, and the office will tell you how much time to set aside when you book."),
        ],
        "related": ["exams-cleanings", "crowns-bridges", "dental-bonding"],
    },
    {
        "slug": "dental-bonding",
        "group": "cosmetic",
        "name": "Dental Bonding",
        "nav": "Bonding",
        "title": "Cosmetic Tooth Bonding in Jupiter, FL | Angelo Forte, DMD",
        "desc": "Repair small chips, cracks and gaps with tooth-colored bonding at Angelo Forte, DMD in Jupiter, FL. Often finished in one visit. Call (561) 747-2134.",
        "h1_lead": "Cosmetic bonding in Jupiter",
        "h1": "A chipped edge, fixed in one sitting.",
        "lede": "Bonding uses tooth-colored resin to repair small chips and cracks, close minor gaps and even out the shape of a tooth. It usually takes one visit and little or no drilling.",
        "short": "Repair small chips, cracks and gaps with tooth-colored resin.",
        "specialty": "Cosmetic dentistry",
        "about": ["Chipped tooth"],
        "sections": [
            ("What bonding is good for", """
<p>Bonding works well for small cosmetic problems: a chipped front tooth, a small crack, a short or uneven tooth, a minor gap, or a stain that whitening won't lift. For larger chips or teeth that need reshaping more dramatically, a porcelain veneer or crown may last longer.</p>"""),
            ("How it is done", """
<p>The surface of the tooth is lightly roughened and conditioned so the resin can grip it. Resin in a shade matched to your teeth is applied in layers, sculpted, hardened with a curing light, then trimmed and polished. Numbing is often unnecessary because little or no tooth structure is removed.</p>"""),
            ("Looking after bonded teeth", """
<p>Bonding resin is strong but not as hard as enamel or porcelain. Avoid biting fingernails, pens or ice with bonded teeth, and expect coffee, tea and red wine to stain it over time. Regular cleanings keep it looking its best, and bonding can be touched up or replaced when it wears.</p>"""),
        ],
        "faqs": [
            ("Is bonding the same as a veneer?", "No. Bonding is resin applied and shaped directly on the tooth, usually in one visit. A porcelain veneer is a thin shell made to fit and then bonded on. Veneers resist staining and wear better; bonding is quicker and less involved."),
            ("Can bonding be whitened?", "Resin does not respond to whitening the way enamel does. If you are planning to whiten, it is usually best to whiten first so the bonding can be matched to your new shade."),
        ],
        "related": ["porcelain-veneers", "teeth-whitening", "fillings"],
    },
    {
        "slug": "crowns-bridges",
        "group": "restorative",
        "name": "Crowns & Bridges",
        "nav": "Crowns & bridges",
        "title": "Dental Crowns & Bridges in Jupiter, FL | Angelo Forte, DMD",
        "desc": "Dental crowns for cracked, broken or heavily filled teeth and bridges to replace missing teeth, from Angelo Forte, DMD in Jupiter, FL. Call (561) 747-2134.",
        "h1_lead": "Crowns & bridges in Jupiter",
        "h1": "When a filling isn't enough.",
        "lede": "A crown covers and protects a tooth that has lost too much structure for a filling. A bridge uses crowns on neighboring teeth to hold a replacement for a missing one.",
        "short": "Protect weak teeth with crowns; replace missing teeth with bridges.",
        "specialty": "Prosthodontics",
        "about": ["Cracked tooth", "Tooth loss"],
        "sections": [
            ("When a crown makes sense", """
<p>Crowns are used for teeth that are cracked, broken, badly worn, or so heavily filled that what is left of the tooth could split. A tooth that has had root canal treatment often needs a crown to protect it. Crowns can also improve the shape and color of a tooth that bonding or a veneer can't fix.</p>"""),
            ("How a crown is made", """
<p>At the first visit the tooth is numbed and shaped, impressions or scans are taken, and a temporary crown goes on to protect it. The permanent crown is made to match the shade and shape of your teeth. At the second visit the temporary comes off, the fit and bite are checked, and the new crown is cemented in place.</p>"""),
            ("Bridges for a missing tooth", """
<p>A traditional bridge spans a gap. The teeth on either side are prepared for crowns, and a replacement tooth is attached between them as one piece. Bridges are fixed in place, so they don't come out like a partial denture. Dr. Forte will compare a bridge with an implant for your situation, because the right choice depends on the health of the neighboring teeth and the bone.</p>"""),
            ("Caring for crowns and bridges", """
<p>Brush and floss as normal. Under a bridge, use a floss threader or interdental brush to clean beneath the replacement tooth, because plaque collects there. Crowns can't decay, but the tooth underneath can, especially along the edge, so regular check-ups still matter.</p>"""),
        ],
        "faqs": [
            ("How long does a dental crown last?", "A well-made crown on a healthy tooth often lasts many years. How long depends on the material, your bite, grinding habits and how well the area is cleaned. Dr. Forte will check it at every exam."),
            ("Is a bridge or an implant better?", "It depends on the teeth next to the gap and the bone where the tooth is missing. A bridge relies on the neighboring teeth; an implant stands on its own. Dr. Forte will explain the trade-offs for your mouth."),
            ("How many visits does a crown take?", "Usually two: one to prepare the tooth and fit a temporary, and one to fit the permanent crown."),
        ],
        "related": ["dental-implants", "root-canal", "fillings"],
    },
    {
        "slug": "dental-implants",
        "group": "replace",
        "name": "Dental Implants",
        "nav": "Implants",
        "title": "Dental Implants in Jupiter, FL | Angelo Forte, DMD",
        "desc": "Dental implants to replace one tooth, several teeth or support dentures, explained by Angelo Forte, DMD in Jupiter, FL. Book a consultation: (561) 747-2134.",
        "h1_lead": "Dental implants in Jupiter",
        "h1": "A replacement tooth that stands on its own.",
        "lede": "An implant replaces the root of a missing tooth, so the new tooth on top is anchored in bone rather than resting on the gum or leaning on its neighbors. The practice describes implants as the longest-lasting tooth replacement available today.",
        "short": "Replace missing teeth with a tooth anchored in the jaw.",
        "specialty": "Prosthodontics",
        "about": ["Tooth loss"],
        "sections": [
            ("How an implant works", """
<p>An implant is a small post, usually titanium, placed in the jawbone where a tooth is missing. Over the following months the bone grows tightly around it. A connector called an abutment is then attached, and a crown is made to sit on top. The result looks and functions much like a natural tooth.</p>
<p>Implants can replace a single tooth, support a bridge where several teeth are missing, or hold a denture firmly in place so it doesn't slip.</p>"""),
            ("Is an implant right for you?", """
<p>Good candidates have healthy gums and enough bone to hold the implant. Smoking, uncontrolled diabetes and some medications can affect healing, and bone that has shrunk after a tooth was lost may need to be built up first. Dr. Forte will review your health history and X-rays and talk through every option, including bridges and dentures, before you commit.</p>"""),
            ("What the process looks like", """
<p>Implant treatment happens in stages over several months: planning, placing the post, healing, then fitting the abutment and final crown. Before treatment starts you will know each stage, who performs it, the timeline and the cost, so there are no surprises halfway through.</p>"""),
            ("Looking after an implant", """
<p>Clean around an implant the same way you would a natural tooth: brushing, flossing or interdental brushes, and regular professional cleanings. Implants can't get cavities, but the gum and bone around them can become inflamed if plaque is left behind.</p>"""),
        ],
        "faqs": [
            ("How long do dental implants last?", "With healthy gums and good cleaning, implants are designed to last for many years. The crown on top may eventually need replacing from normal wear."),
            ("Am I too old for an implant?", "Age alone usually isn't the deciding factor. Overall health, bone and gum health matter more. Dr. Forte will assess this at a consultation."),
            ("Does insurance cover implants?", "Coverage varies a lot between plans. The office will help you check your benefits and file the claim, and CareCredit financing is available for costs your insurance doesn't cover."),
        ],
        "related": ["crowns-bridges", "dentures", "tooth-extraction"],
    },
    {
        "slug": "porcelain-veneers",
        "group": "cosmetic",
        "name": "Porcelain Veneers",
        "nav": "Veneers",
        "title": "Porcelain Veneers in Jupiter, FL | Angelo Forte, DMD",
        "desc": "Porcelain veneers to repair chips and cracks, close gaps and reshape front teeth, from cosmetic dentist Angelo Forte, DMD in Jupiter, FL. (561) 747-2134.",
        "h1_lead": "Porcelain veneers in Jupiter",
        "h1": "Change the shape and shade of your smile.",
        "lede": "Veneers are thin shells of porcelain bonded to the front of the teeth. They repair larger chips and cracks, close gaps, and change the shape and color of teeth in a way whitening alone can't.",
        "short": "Repair larger chips and cracks and reshape front teeth.",
        "specialty": "Cosmetic dentistry",
        "about": ["Tooth discoloration", "Chipped tooth"],
        "sections": [
            ("What veneers can change", """
<p>Veneers cover the visible front surface of a tooth. They suit teeth that are chipped, cracked, worn short, slightly crooked, unevenly spaced, or stained in a way bleaching can't reach. Porcelain resists staining and reflects light much like enamel does.</p>"""),
            ("The process", """
<p>It starts with a conversation about what you want to change and a careful look at your teeth, gums and bite. To make room for the porcelain, a thin layer of enamel is usually removed from the front of each tooth, and impressions or scans are taken. Temporaries may be placed while the veneers are made. At the fitting visit each veneer is checked, adjusted and bonded in place.</p>"""),
            ("Things to know first", """
<p>Because enamel is removed, veneers are generally considered permanent. They can chip if used to bite very hard things, and people who grind their teeth may need a night guard to protect them. If your gums need treatment or you have active decay, that comes first. Bonding is a quicker, less involved alternative for small fixes.</p>"""),
        ],
        "faqs": [
            ("How long do porcelain veneers last?", "Veneers often last many years with good care. Grinding, biting hard objects and gum health all affect how long they last."),
            ("Do veneers look natural?", "Porcelain is translucent like enamel, and each veneer is made to match the shape and shade you choose with Dr. Forte, so they are designed to look like your own teeth."),
            ("Should I whiten before veneers?", "If you want your other teeth lighter too, whitening first lets the veneers be matched to your brighter shade."),
        ],
        "related": ["teeth-whitening", "dental-bonding", "crowns-bridges"],
    },
    {
        "slug": "teeth-whitening",
        "group": "cosmetic",
        "name": "Teeth Whitening",
        "nav": "Whitening",
        "title": "Teeth Whitening in Jupiter, FL | Angelo Forte, DMD",
        "desc": "Professional teeth whitening for stained, dull or discolored teeth at Angelo Forte, DMD in Jupiter, FL. What it can and can't do, and how long it lasts. (561) 747-2134.",
        "h1_lead": "Teeth whitening in Jupiter",
        "h1": "A brighter smile, supervised by a dentist.",
        "lede": "Professional whitening lifts stains from coffee, tea, red wine, tobacco and age. Having a dentist oversee it means the shade change is planned and your gums and sensitive teeth are looked after.",
        "short": "Brighten stained, dull or discolored teeth.",
        "specialty": "Cosmetic dentistry",
        "about": ["Tooth discoloration"],
        "sections": [
            ("What whitening can and can't do", """
<p>Whitening works on natural enamel. It is very effective on yellowing and surface staining from food, drink and smoking. It does not change the color of fillings, crowns, veneers or bonding, and some deep internal stains respond poorly. If that's your situation, bonding or veneers may be the better route, and Dr. Forte will say so.</p>"""),
            ("Before you whiten", """
<p>A check-up and cleaning come first. Whitening a tooth with a cavity or leaking filling can be painful, and removing surface stain at a cleaning shows what color your teeth really are. Dr. Forte will note your starting shade so you can see the change.</p>"""),
            ("Sensitivity and upkeep", """
<p>Some people feel temporary sensitivity during or shortly after whitening. It usually fades within a few days. Results fade gradually too, faster with coffee, tea, red wine and smoking; occasional touch-ups keep the shade where you want it.</p>"""),
        ],
        "faqs": [
            ("Does teeth whitening damage enamel?", "Whitening carried out as directed under a dentist's supervision is generally considered safe for enamel. Temporary sensitivity is the most common side effect."),
            ("Will whitening work on my crowns or veneers?", "No. Whitening only changes natural tooth enamel. Crowns, veneers, fillings and bonding keep their original shade."),
            ("How long does whitening last?", "It varies with diet and habits. Coffee, tea, red wine and tobacco bring stain back sooner. Touch-ups maintain the result."),
        ],
        "related": ["porcelain-veneers", "dental-bonding", "exams-cleanings"],
    },
    {
        "slug": "invisalign",
        "group": "cosmetic",
        "name": "Invisalign & Orthodontics",
        "nav": "Invisalign",
        "title": "Invisalign Clear Aligners in Jupiter, FL | Angelo Forte, DMD",
        "desc": "Straighten crooked or crowded teeth with Invisalign clear aligners and orthodontic treatment at Angelo Forte, DMD in Jupiter, FL. Call (561) 747-2134.",
        "h1_lead": "Invisalign in Jupiter",
        "h1": "Straighter teeth without a mouthful of metal.",
        "lede": "Invisalign uses a series of clear, removable aligners to move teeth gradually into a better position. Straighter teeth are easier to clean and can bite together more evenly.",
        "short": "Straighten teeth with clear, removable aligners.",
        "specialty": "Orthodontics",
        "about": ["Malocclusion"],
        "sections": [
            ("How clear aligners work", """
<p>Each set of aligners is shaped slightly differently from the last. Worn for most of the day and night, each set nudges the teeth a little further before you move on to the next. Because they come out, you can eat what you like and brush and floss normally.</p>"""),
            ("Who it suits", """
<p>Clear aligners work well for many adults and teens with crowding, spacing and some bite problems. More complex cases may be better treated with traditional braces or by an orthodontist. Dr. Forte will look at your teeth and tell you honestly which approach fits.</p>"""),
            ("Making it work", """
<p>Aligners only move teeth while they are in, so wearing them for the recommended hours each day matters more than anything else. After treatment, a retainer holds the teeth in their new position; without one, teeth tend to drift back.</p>"""),
        ],
        "faqs": [
            ("How many hours a day do I wear Invisalign aligners?", "Aligners are generally worn for most of the day and night and removed to eat, drink anything other than water, and clean your teeth. Dr. Forte will give you the target for your treatment."),
            ("Do I need a retainer afterwards?", "Yes. Teeth naturally try to move back, and a retainer keeps them where treatment put them."),
            ("Can adults get Invisalign?", "Yes. Many people who straighten their teeth with clear aligners are adults."),
        ],
        "related": ["porcelain-veneers", "teeth-whitening", "tmj-treatment"],
    },
    {
        "slug": "root-canal",
        "group": "relief",
        "name": "Root Canal Treatment",
        "nav": "Root canals",
        "title": "Root Canal Treatment in Jupiter, FL | Angelo Forte, DMD",
        "desc": "Root canal treatment to save an infected or badly inflamed tooth at Angelo Forte, DMD in Jupiter, FL. Signs to watch for and what to expect. (561) 747-2134.",
        "h1_lead": "Root canal treatment in Jupiter",
        "h1": "Keep the tooth, lose the toothache.",
        "lede": "Root canal treatment removes infected or inflamed tissue from inside a tooth, cleans and seals it, and lets you keep the tooth instead of having it pulled.",
        "short": "Save an infected tooth instead of removing it.",
        "specialty": "Endodontics",
        "about": ["Pulpitis", "Dental abscess"],
        "sections": [
            ("Signs a tooth may need a root canal", """
<p>Deep decay, a crack or an injury can let bacteria reach the pulp, the soft tissue inside the tooth. Warning signs include a throbbing toothache, pain when biting, sensitivity to hot or cold that lingers after the drink is gone, a tooth that has darkened, or a pimple-like bump on the gum. Some infected teeth cause no pain at all and only show on an X-ray.</p>"""),
            ("What the treatment involves", """
<p>The tooth is numbed and an opening is made in the top. The infected tissue is removed, the canals inside the roots are cleaned and shaped, then filled and sealed. Most patients say it feels much like having a filling. Because a treated back tooth can become brittle, a crown is often recommended afterwards to protect it.</p>"""),
            ("Why not just pull it?", """
<p>Keeping your natural tooth keeps the neighboring teeth from drifting into the gap and avoids the cost and time of replacing it. Sometimes a tooth can't be saved, and then an extraction followed by an implant, bridge or denture is the better plan. Dr. Forte will explain which applies to you.</p>"""),
        ],
        "faqs": [
            ("Is a root canal painful?", "The tooth is fully numbed during treatment. Most of the pain people associate with root canals comes from the infection beforehand, and treatment relieves it. Some tenderness for a few days afterwards is normal."),
            ("Do I need a crown after a root canal?", "Often, especially on back teeth that take heavy chewing forces. Dr. Forte will tell you if your tooth needs one."),
            ("Can an abscessed tooth go away on its own?", "No. Antibiotics can calm an infection temporarily, but the source inside the tooth stays until it is treated. Call the office if you have swelling or a painful bump on your gum."),
        ],
        "related": ["emergency-dentist", "crowns-bridges", "tooth-extraction"],
    },
    {
        "slug": "gum-disease-treatment",
        "group": "preventive",
        "name": "Gum Disease Treatment",
        "nav": "Gum disease",
        "title": "Gum Disease Treatment in Jupiter, FL | Angelo Forte, DMD",
        "desc": "Periodontal (gum) disease therapy to stop bleeding gums and prevent tooth loss, at Angelo Forte, DMD in Jupiter, FL. Know the warning signs. (561) 747-2134.",
        "h1_lead": "Gum disease treatment in Jupiter",
        "h1": "Bleeding gums are a reason to call.",
        "lede": "Gum disease is an infection of the tissue and bone that hold your teeth in place. It is a leading cause of tooth loss in adults, and the practice treats it to keep that from happening.",
        "short": "Periodontal therapy to stop gum disease and prevent tooth loss.",
        "specialty": "Periodontics",
        "about": ["Periodontal disease", "Gingivitis"],
        "sections": [
            ("Warning signs", """
<p>Gums that bleed when you brush or floss, are red, swollen or tender, or have pulled back from the teeth. Persistent bad breath or a bad taste. Teeth that feel loose or have changed how they fit together. Gum disease often doesn't hurt, which is why many people don't know they have it.</p>"""),
            ("From gingivitis to periodontitis", """
<p>The early stage, gingivitis, affects only the gums and can usually be reversed with a professional cleaning and better daily cleaning at home. Left alone, it can progress to periodontitis, where the infection damages the bone that supports the teeth and pockets form between the gums and teeth.</p>"""),
            ("How it is treated", """
<p>Treatment depends on how far the disease has gone. A common first step is scaling and root planing, a deep cleaning below the gumline that removes tartar and smooths the root surfaces so the gums can heal and reattach. More frequent maintenance cleanings usually follow. Advanced cases may need referral to a periodontist, and Dr. Forte will tell you if yours does.</p>"""),
            ("Your gums and your general health", """
<p>The practice's approach is to treat the whole person, with particular attention to how your teeth and gums relate to your overall health. Research has linked gum disease with other conditions, including diabetes and heart disease, so keeping your gums healthy is about more than your smile. Tell Dr. Forte about your medical history and medications; they affect how your gums behave.</p>"""),
        ],
        "faqs": [
            ("Is it normal for gums to bleed when I floss?", "Occasional bleeding is common, but regular bleeding is one of the first signs of gum inflammation. Have it checked; early gum disease is usually reversible."),
            ("What is a deep cleaning?", "Scaling and root planing cleans below the gumline, removing tartar from the roots and smoothing them so the gums can heal. It is usually done with the area numbed."),
            ("Can gum disease be cured?", "Gingivitis can usually be reversed. Periodontitis can be controlled and its progress stopped with treatment and regular maintenance, but bone that has been lost does not simply grow back."),
        ],
        "related": ["exams-cleanings", "dental-implants", "tooth-extraction"],
    },
    {
        "slug": "dentures",
        "group": "replace",
        "name": "Dentures",
        "nav": "Dentures",
        "title": "Full & Partial Dentures in Jupiter, FL | Angelo Forte, DMD",
        "desc": "Removable full and partial dentures, and implant options for a firmer fit, from Angelo Forte, DMD in Jupiter, FL. Call (561) 747-2134 to talk it through.",
        "h1_lead": "Dentures in Jupiter",
        "h1": "Eat, speak and smile with confidence again.",
        "lede": "Removable dentures replace missing teeth and the gum around them. A full denture replaces a whole arch; a partial fills the gaps between your remaining teeth.",
        "short": "Removable full and partial dentures to replace missing teeth.",
        "specialty": "Prosthodontics",
        "about": ["Tooth loss", "Edentulism"],
        "sections": [
            ("Full or partial", """
<p>A <strong>full denture</strong> replaces all the teeth in the upper or lower jaw and rests on the gums. A <strong>partial denture</strong> clips to your remaining natural teeth and fills the spaces, which also stops those teeth from drifting. Where the bone allows, dental implants can anchor a denture so it doesn't slip when you eat or talk.</p>"""),
            ("Getting used to new dentures", """
<p>Expect a few weeks of adjustment. Eating and speaking can feel strange at first; start with soft foods cut small, and read aloud to get used to talking. Sore spots are common early on and are easy to adjust, so call rather than putting up with them.</p>"""),
            ("Care and check-ups", """
<p>Clean dentures every day with a denture brush and cleaner, not regular toothpaste, which can scratch them. Take them out at night unless Dr. Forte advises otherwise, and keep them moist. Your mouth changes shape over time, so dentures need periodic checks and may need relining to stay comfortable.</p>"""),
        ],
        "faqs": [
            ("How long does it take to get used to dentures?", "Most people adapt over a few weeks. Sore spots are normal early on and can be adjusted at the office."),
            ("Can dentures be made to fit more securely?", "Yes. Relining can improve the fit as your mouth changes, and implants can anchor a denture for a much firmer hold. Dr. Forte will tell you whether implants are an option for you."),
        ],
        "related": ["dental-implants", "crowns-bridges", "tooth-extraction"],
    },
    {
        "slug": "tooth-extraction",
        "group": "relief",
        "name": "Tooth Extraction",
        "nav": "Extractions",
        "title": "Tooth Extractions in Jupiter, FL | Angelo Forte, DMD",
        "desc": "Gentle tooth extractions in Jupiter, FL when a tooth is too damaged or decayed to save, plus aftercare and replacement options. Angelo Forte, DMD: (561) 747-2134.",
        "h1_lead": "Tooth extraction in Jupiter",
        "h1": "When a tooth can't be saved.",
        "lede": "Dr. Forte's first goal is to keep your natural teeth. When a tooth is too broken or decayed to repair, removing it relieves pain, stops infection spreading and clears the way for a replacement.",
        "short": "Remove a tooth that is too damaged or decayed to repair.",
        "specialty": "Oral surgery",
        "about": ["Tooth decay"],
        "sections": [
            ("Why a tooth may need to come out", """
<p>Common reasons include a tooth broken below the gumline, decay too extensive for a filling or crown, advanced gum disease that has loosened a tooth, or an infection that can't be treated with a root canal. Teeth are sometimes removed to make room for orthodontic treatment, and wisdom teeth can cause problems when there isn't space for them.</p>"""),
            ("What to expect", """
<p>The area is numbed thoroughly. You will feel pressure as the tooth is loosened and removed, but you shouldn't feel sharp pain. A blood clot forms in the socket, which is the start of healing. Some extractions, such as impacted wisdom teeth, may be referred to an oral surgeon.</p>"""),
            ("Aftercare", """
<p>Bite on gauze for the time you are told and rest for the remainder of the day. For the first day or so avoid rinsing hard, spitting, drinking through a straw and smoking, all of which can dislodge the clot and cause a painful dry socket. Stick to soft foods and follow the instructions you are given. Call the office if bleeding, swelling or pain gets worse instead of better.</p>"""),
            ("Replacing the tooth", """
<p>Leaving a gap can let neighboring teeth tip and drift, and the bone in the area slowly shrinks. Dr. Forte will discuss an implant, bridge or partial denture with you, ideally before the extraction, so you know the whole plan.</p>"""),
        ],
        "faqs": [
            ("Does a tooth extraction hurt?", "The area is numbed, so you should feel pressure rather than pain during the extraction. Soreness for a few days afterwards is normal and is usually managed with over-the-counter pain relief as directed."),
            ("What is a dry socket?", "It happens when the blood clot in the socket is lost too early, exposing the bone. It is painful but treatable. Avoiding straws, smoking and hard rinsing in the first days helps prevent it."),
        ],
        "related": ["dental-implants", "dentures", "root-canal"],
    },
    {
        "slug": "tmj-treatment",
        "group": "relief",
        "name": "TMJ / TMD Treatment",
        "nav": "TMJ & jaw pain",
        "title": "TMJ & Jaw Pain Treatment in Jupiter, FL | Angelo Forte, DMD",
        "desc": "Treatment for TMJ disorders: jaw pain, clicking, headaches and teeth grinding, at Angelo Forte, DMD in Jupiter, FL. Call (561) 747-2134 to be seen.",
        "h1_lead": "TMJ & TMD treatment in Jupiter",
        "h1": "Jaw pain shouldn't be part of your day.",
        "lede": "Temporomandibular disorders (TMD) affect the jaw joints and the muscles that move them. They can cause chronic jaw pain, clicking, headaches and trouble opening wide. The practice treats TMJ and TMD for chronic jaw pain.",
        "short": "Relief for chronic jaw pain, clicking and grinding.",
        "specialty": "Dentistry",
        "about": ["Temporomandibular joint disorder", "Bruxism"],
        "sections": [
            ("Common symptoms", """
<p>Aching in the jaw, face or around the ear; clicking, popping or grating when you open your mouth; a jaw that locks or won't open fully; headaches, especially on waking; and worn, chipped or sensitive teeth from clenching or grinding at night.</p>"""),
            ("What causes it", """
<p>TMD often has more than one cause. Clenching and grinding (bruxism), stress, an uneven bite, arthritis in the joint and injury can all play a part. Working out which factors apply to you is the first step, so Dr. Forte will examine the joints, muscles, teeth and bite and ask about your symptoms and habits.</p>"""),
            ("Treatment options", """
<p>Most TMD improves with conservative care. That can include a custom night guard or splint to protect the teeth and relax the muscles, adjusting high spots in the bite, jaw exercises, and changes such as softer foods and avoiding gum. If your symptoms point to a joint problem that needs specialist care, you will be referred.</p>"""),
        ],
        "faqs": [
            ("Can a dentist treat TMJ pain?", "Yes. Dentists commonly diagnose and treat TMD, often with a custom night guard or splint and bite adjustment. Complex joint problems may be referred to a specialist."),
            ("Will a night guard stop me grinding?", "A night guard doesn't always stop the habit, but it protects your teeth from wear and can ease the strain on your jaw muscles and joints."),
        ],
        "related": ["exams-cleanings", "invisalign", "emergency-dentist"],
    },
    {
        "slug": "emergency-dentist",
        "group": "relief",
        "name": "Emergency Dental Care",
        "nav": "Emergency dentist",
        "title": "Emergency Dentist in Jupiter, FL | Angelo Forte, DMD",
        "desc": "Toothache, broken or knocked-out tooth in Jupiter, FL? Call Angelo Forte, DMD at (561) 747-2134. What to do right now, and when to go to the ER instead.",
        "h1_lead": "Emergency dentist in Jupiter",
        "h1": "Broken, knocked out or throbbing? Call us.",
        "lede": "The practice treats a range of dental injuries, including teeth that have been chipped, moved or knocked out entirely. Call (561) 747-2134 and the office will help you.",
        "short": "Toothaches, broken teeth and knocked-out teeth.",
        "specialty": "Dentistry",
        "about": ["Toothache", "Tooth avulsion", "Dental abscess"],
        "sections": [
            ("Go to the ER first if", """
<p>If you have a life-threatening or severe injury, call 911 or go straight to the nearest hospital emergency room. That includes a blow to the head, uncontrolled bleeding, trouble breathing or swallowing, or swelling that is spreading to your eye or neck. Jupiter Medical Center is about 1.4 miles from the office.</p>"""),
            ("A knocked-out adult tooth", """
<p>Time matters. Pick the tooth up by the crown (the white part), not the root. If it is dirty, rinse it briefly with milk or water without scrubbing. If you can, gently push it back into the socket and bite on a clean cloth to hold it. If not, keep it in a cup of milk or tucked inside your cheek, and call the office straight away. Don't try to put a baby tooth back in.</p>"""),
            ("A chipped or broken tooth", """
<p>Rinse your mouth with warm water and save any pieces. Hold a cold compress against your cheek to limit swelling. If a sharp edge is cutting your tongue, a piece of sugar-free gum or dental wax can cover it until you are seen.</p>"""),
            ("A bad toothache or swelling", """
<p>Rinse with warm salt water and floss gently to remove anything caught between the teeth. Over-the-counter pain relief taken as directed on the packet can help; never put aspirin directly on the gum. Swelling, fever or a bad taste can mean infection, so call the office promptly.</p>"""),
            ("Outside office hours", """
<p>Office hours are Monday to Thursday, 8:00 AM to 5:00 PM, with Friday by appointment. If it is after hours, call (561) 747-2134 and follow the instructions on the office's message. For a severe injury, don't wait: call 911 or go to the ER.</p>"""),
        ],
        "faqs": [
            ("What counts as a dental emergency?", "A knocked-out or loosened adult tooth, a broken tooth with pain, a severe toothache, swelling in the face or gums, or bleeding that won't stop. Severe facial injuries and swelling that affects breathing or swallowing need the ER first."),
            ("What should I do with a knocked-out tooth?", "Hold it by the crown, rinse it briefly without scrubbing, and either place it back in the socket or keep it in milk. Then call the office immediately; the sooner it is seen, the better the chance of saving it."),
            ("Can I go to urgent care for a toothache?", "Urgent care and ER doctors can help with pain, swelling and infection, but they can't repair the tooth. Call the dental office so the cause can be treated."),
        ],
        "related": ["root-canal", "tooth-extraction", "crowns-bridges"],
    },
]

# --- Intent cards on the homepage ---------------------------------------------
INTENTS = [
    ("Something hurts", "A toothache, swelling, or a tooth that broke at dinner.", "emergency-dentist"),
    ("I'm due a check-up", "Cleanings, exams, X-rays and an oral cancer screening.", "exams-cleanings"),
    ("A tooth is missing", "Implants, bridges and dentures, side by side.", "dental-implants"),
    ("I want a brighter smile", "Whitening, bonding and porcelain veneers.", "teeth-whitening"),
    ("My teeth are crooked", "Clear aligners that come out when you eat.", "invisalign"),
    ("My jaw clicks or aches", "TMJ and TMD care, including night guards.", "tmj-treatment"),
]

# --- General FAQ (rendered on /faq/, a subset on the homepage) -----------------
FAQS = [
    ("Is Angelo Forte, DMD taking new patients?", "Yes. Call (561) 747-2134 to book a first visit. The office will take your details and insurance information over the phone."),
    ("Where is the office?", "654 W. Indiantown Rd., Suite 105, Jupiter, FL 33458, on Indiantown Road a short distance east of Military Trail. Harbourside Place and Jupiter Medical Center are both under two miles away."),
    ("What are your office hours?", "Monday to Thursday, 8:00 AM to 5:00 PM, closed for lunch from 1:00 to 2:00 PM. Friday is by appointment only. The office is closed on Saturday and Sunday."),
    ("Do you accept my dental insurance?", "The practice accepts most traditional insurance plans and will file your claims for you. It does not participate in HMO plans. Call the office with your plan details and they will check it for you."),
    ("Can I see you if you're out of network for my plan?", "In many cases, yes. If your plan lets you choose your own dentist, the office is happy to file your insurance for reimbursement. Call to check how your plan handles out-of-network care."),
    ("How can I pay?", "Cash, check and credit cards. The practice also offers a flexible payment plan; ask the Financial Coordinator for details. CareCredit financing is accepted for costs insurance doesn't cover."),
    ("Do you treat children?", "The practice cares for the whole family, and its preventive services include sealants to protect children's teeth from decay."),
    ("What should I bring to my first visit?", "Your insurance card and photo ID, a list of the medications you take, and any recent dental X-rays from a previous dentist if you have them. Arriving a little early gives time for paperwork."),
    ("What should I do in a dental emergency?", "Call (561) 747-2134. For a severe injury, uncontrolled bleeding, or swelling that affects breathing or swallowing, call 911 or go to the nearest emergency room first. Our emergency page explains what to do with a knocked-out or broken tooth."),
    ("Do you offer Invisalign?", "Yes. Invisalign is listed among the practice's equipment, and orthodontic treatment is one of its services."),
    ("Do you use digital X-rays?", "Yes. Images are ready on screen straight away, so Dr. Forte can show you what he sees."),
    ("If I can't make my appointment, what should I do?", "Call the office as soon as you can if you need to cancel or will be running late, so the time can be offered to someone else."),
]

# Homepage shows these five (indexes into FAQS); the full set lives on /faq/.
HOME_FAQ_PICK = [0, 3, 5, 2, 8]

# /faq/ topics: (anchor, heading, one-line intro, general FAQ indexes, service slugs whose FAQs join it).
# Every general FAQ and every service FAQ appears exactly once.
FAQ_CATEGORIES = [
    ("visits", "Appointments & first visits", "Booking, hours, what to bring and where to find the office.", [0, 1, 2, 7, 11], []),
    ("insurance", "Insurance & payment", "Plans, out-of-network claims, payment options and financing.", [3, 4, 5], []),
    ("emergencies", "Dental emergencies", "Toothaches, broken and knocked-out teeth, and when to go to the ER.", [8], ["emergency-dentist"]),
    ("preventive", "Cleanings, exams & gum health", "Check-ups, X-rays, oral cancer screening, sealants and gum disease.", [6, 10], ["exams-cleanings", "gum-disease-treatment"]),
    ("repairs", "Fillings, crowns & root canals", "Fixing cavities, cracked teeth and infected teeth.", [], ["fillings", "crowns-bridges", "root-canal"]),
    ("cosmetic", "Whitening, veneers & Invisalign", "Brightening, reshaping and straightening your smile.", [9], ["teeth-whitening", "porcelain-veneers", "dental-bonding", "invisalign"]),
    ("replacement", "Implants, dentures & extractions", "Replacing missing teeth, and when a tooth has to come out.", [], ["dental-implants", "dentures", "tooth-extraction"]),
    ("jaw", "TMJ & jaw pain", "Clicking, aching jaws and teeth grinding.", [], ["tmj-treatment"]),
]

# --- Areas served ---------------------------------------------------------------
# Distances and routes: OSRM routing over OpenStreetMap from each town's center to
# the office, 2026-10-19. Road names translated from route refs: SR 706 = Indiantown
# Road, CR 809 = Military Trail, SR 811 = Alternate A1A, SR 786 = PGA Boulevard.
AREAS = [
    {
        "slug": "tequesta",
        "name": "Tequesta",
        "miles": 2.7, "minutes": 6,
        "route": "Head south on Old Dixie Highway, pick up Alternate A1A, then turn west onto Indiantown Road. The office is on the right before you reach Military Trail.",
        "intro": "Tequesta sits just across the Loxahatchee River from Jupiter, close enough that a cleaning fits into a lunch break.",
        "notes": [
            "The drive is under three miles from central Tequesta, mostly along Old Dixie Highway and Alternate A1A.",
            "The first appointments of the day start at 8:00 AM, Monday to Thursday.",
            "For a dental injury out of hours, Jupiter Medical Center is about a mile and a half from the office.",
        ],
    },
    {
        "slug": "juno-beach",
        "name": "Juno Beach",
        "miles": 5.6, "minutes": 10,
        "route": "Take US-1 north out of Juno Beach toward Jupiter, then turn west onto Indiantown Road. The office is a little under a mile along, past Alternate A1A.",
        "intro": "From Juno Beach the office is a straight run up US-1, roughly ten minutes when the road is clear.",
        "notes": [
            "The route is almost entirely US-1, so there is no need to cut inland to Military Trail.",
            "Juno Beach Pier is about five miles from the office, roughly ten minutes by car outside rush hour.",
        ],
    },
    {
        "slug": "abacoa",
        "name": "Abacoa",
        "miles": 4.0, "minutes": 8,
        "route": "Leave Abacoa on University Boulevard, turn north onto Military Trail, then east onto Indiantown Road. The office is just past the Military Trail intersection.",
        "intro": "Abacoa is a Jupiter neighborhood, and the office is a short drive north up Military Trail.",
        "notes": [
            "From Abacoa Town Center it is about four miles, nearly all of it on Military Trail.",
            "Because the office sits just east of Military Trail on Indiantown Road, there is no need to cross Alternate A1A or US-1.",
        ],
    },
    {
        "slug": "jupiter-farms",
        "name": "Jupiter Farms",
        "miles": 8.3, "minutes": 18,
        "route": "Make your way to Indiantown Road and head east, crossing the Turnpike and I-95, then continue past Military Trail. The office is on Indiantown Road just beyond it.",
        "intro": "From Jupiter Farms, Indiantown Road takes you almost all the way here.",
        "notes": [
            "Most of the trip is a single road: Indiantown Road east from the Jupiter Farms area.",
            "Allow extra time around the I-95 and Turnpike interchanges at busy times of day.",
            "Riverbend Park, off Indiantown Road west of I-95, is a little over five miles from the office.",
        ],
    },
    {
        "slug": "palm-beach-gardens",
        "name": "Palm Beach Gardens",
        "miles": 10.7, "minutes": 22,
        "route": "From central Palm Beach Gardens take PGA Boulevard to Military Trail, head north on Military Trail all the way to Indiantown Road, then turn east. The office is just past the intersection.",
        "intro": "Palm Beach Gardens patients usually reach the office by heading north on Military Trail, which ends a short way from the door.",
        "notes": [
            "Military Trail runs north from PGA Boulevard to Indiantown Road, so the route has only a couple of turns.",
            "Allow longer during the afternoon rush on PGA Boulevard and Military Trail.",

        ],
    },
    {
        "slug": "north-palm-beach",
        "name": "North Palm Beach",
        "miles": 10.0, "minutes": 18,
        "route": "Take US-1 north through Juno Beach into Jupiter, then turn west onto Indiantown Road. The office is a little under a mile along.",
        "intro": "From North Palm Beach the office is a straight drive north on US-1 and a short hop west on Indiantown Road.",
        "notes": [
            "US-1 carries you almost the whole way; the last mile is on Indiantown Road.",
            "Expect about twenty minutes outside rush hour.",

        ],
    },
    {
        "slug": "hobe-sound",
        "name": "Hobe Sound",
        "miles": 11.9, "minutes": 20,
        "route": "Head south on US-1 from Hobe Sound into Tequesta, take Alternate A1A south, then turn west onto Indiantown Road. The office is less than a mile along.",
        "intro": "Hobe Sound is in Martin County, but the office is only about twenty minutes south down US-1.",
        "notes": [
            "The route follows US-1 through Tequesta before joining Alternate A1A and Indiantown Road.",
            "Coming from the island side of Hobe Sound, County Road A1A joins US-1 on the way south.",
            "The first appointments of the day start at 8:00 AM, Monday to Thursday.",
        ],
    },
]
