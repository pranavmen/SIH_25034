// recommender/static/recommender/script.js

// --- DOM Elements ---
const wizardForm = document.getElementById('wizard-form');
const submitBtn = document.getElementById('submit-btn');
const loader = document.getElementById('loader');
const resultsArea = document.getElementById('results-area');
const resultsContainer = document.getElementById('results-container');
const skillsContainer = document.getElementById('skills-container');
const interestsContainer = document.getElementById('interests-container');
const progressBar = document.getElementById('progress-bar');
const steps = document.querySelectorAll('.step');
const totalSteps = steps.length - 1;
const langToggleBtn = document.getElementById('lang-toggle');

// --- Translations ---
const translations = {
    en: {
        main_title: "Find Your Perfect Internship ✨",
        main_subtitle: "Answer a few questions to get 3-5 personalized recommendations.",
        welcome_title: "Welcome!",
        welcome_subtitle: "Let's get started. It only takes a minute.",
        start_now_btn: "Start Now",
        edu_title: "🎓 Your Education",
        edu_q1: "What is your highest qualification?",
        edu_q2: "What is your field of study?",
        wfh_checkbox: "Show me Work From Home internships only",
        skills_title: "💡 Your Skills",
        skills_subtitle: "Select a few skills you have (or want to learn).",
        interests_title: "🎯 Your Interests",
        interests_subtitle: "Which sectors are you interested in?",
        location_title: "📍 Location Preference",
        location_q1: "Where would you like to work?",
        back_btn: "Back",
        next_btn: "Next",
        find_btn: "Find Internships",
        loader_text: "Finding the best matches for you...",
        results_title: "🚀 Here are your top matches!",
        next_title: "🤔 What should I do next?",
        next_step1: "📄 **Prepare Your Resume:** Make sure your contact details are correct.",
        next_step2: "✉️ **Click \"View & Apply\":** This will open a simple summary. Review it and then proceed to the company's application page.",
        next_step3: "💡 **Be Confident:** Your skills and interests are a great match for these roles!",
        feedback_title: "Were these recommendations helpful?",
        feedback_thanks: "Thank you for your feedback!",
        modal_role: "Your Role:",
        proceed_btn: "Proceed to Apply",
        // Options
        btech: "B.Tech / B.E.", ba: "B.A.", bcom: "B.Com", bsc: "B.Sc", polytechnic: "Polytechnic / Diploma", other: "Other",
        cs: "Computer Science", mech: "Mechanical Engineering", electronics: "Electronics", commerce: "Commerce", arts: "Arts",
        skill_comm: "Communication", skill_team: "Teamwork", skill_python: "Python", skill_java: "Java", skill_mktg: "Marketing", skill_sales: "Sales", skill_office: "MS Office", skill_data: "Data Analysis",
        interest_it: "IT & Software", interest_mktg: "Marketing & Sales", interest_engg: "Core Engineering", interest_finance: "Finance",
        loc_any: "Any Location", loc_pune: "Pune", loc_mumbai: "Mumbai", loc_delhi: "Delhi", loc_bangalore: "Bangalore", loc_wfh: "Work From Home"
    },
    hi: {
        main_title: "अपनी परफेक्ट इंटर्नशिप ढूंढें ✨",
        main_subtitle: "3-5 वैयक्तिकृत सिफारिशें प्राप्त करने के लिए कुछ सवालों के जवाब दें।",
        welcome_title: "आपका स्वागत है!",
        welcome_subtitle: "चलिए शुरू करते हैं। इसमें केवल एक मिनट लगेगा।",
        start_now_btn: "अभी शुरू करें",
        edu_title: "🎓 आपकी शिक्षा",
        edu_q1: "आपकी उच्चतम योग्यता क्या है?",
        edu_q2: "आपके अध्ययन का क्षेत्र क्या है?",
        wfh_checkbox: "मुझे केवल घर से काम करने वाली इंटर्नशिप दिखाएं",
        skills_title: "💡 आपके कौशल",
        skills_subtitle: "आपके पास कुछ कौशल चुनें (या सीखना चाहते हैं)।",
        interests_title: "🎯 आपकी रुचियां",
        interests_subtitle: "आप किन क्षेत्रों में रुचि रखते हैं?",
        location_title: "📍 स्थान वरीयता",
        location_q1: "आप कहाँ काम करना चाहेंगे?",
        back_btn: "वापस",
        next_btn: "अगला",
        find_btn: "इंटर्नशिप खोजें",
        loader_text: "आपके लिए सबसे अच्छे मैच ढूंढ रहे हैं...",
        results_title: "🚀 यहाँ आपके शीर्ष मैच हैं!",
        next_title: "🤔 मुझे आगे क्या करना चाहिए?",
        next_step1: "📄 **अपना रिज्यूमे तैयार करें:** सुनिश्चित करें कि आपके संपर्क विवरण सही हैं।",
        next_step2: "✉️ **\"देखें और आवेदन करें\" पर क्लिक करें:** यह एक सरल सारांश खोलेगा। इसकी समीक्षा करें और फिर कंपनी के आवेदन पृष्ठ पर आगे बढ़ें।",
        next_step3: "💡 **आत्मविश्वासी बनें:** आपके कौशल और रुचियां इन भूमिकाओं के लिए एक बढ़िया मेल हैं!",
        feedback_title: "क्या ये सिफारिशें सहायक थीं?",
        feedback_thanks: "आपकी प्रतिक्रिया के लिए धन्यवाद!",
        modal_role: "आपकी भूमिका:",
        proceed_btn: "आवेदन करने के लिए आगे बढ़ें",
        // Options
        btech: "बी.टेक / बी.ई.", ba: "बी.ए.", bcom: "बी.कॉम", bsc: "बी.एससी", polytechnic: "पॉलिटेक्निक / डिप्लोमा", other: "अन्य",
        cs: "कंप्यूटर विज्ञान", mech: "मैकेनिकल इंजीनियरिंग", electronics: "इलेक्ट्रानिक्स", commerce: "व्यापार", arts: "कला",
        skill_comm: "संचार", skill_team: "टीम वर्क", skill_python: "पाइथन", skill_java: "जावा", skill_mktg: "विपणन", skill_sales: "बिक्री", skill_office: "एमएस ऑफिस", skill_data: "डेटा विश्लेषण",
        interest_it: "आईटी और सॉफ्टवेयर", interest_mktg: "विपणन और बिक्री", interest_engg: "कोर इंजीनियरिंग", interest_finance: "वित्त",
        loc_any: "कोई भी स्थान", loc_pune: "पुणे", loc_mumbai: "मुंबई", loc_delhi: "दिल्ली", loc_bangalore: "बैंगलोर", loc_wfh: "घर से काम"
    }
};

let currentLang = 'en';

// --- Language Switching ---
const updateContent = () => {
    document.querySelectorAll('[data-key]').forEach(element => {
        const key = element.getAttribute('data-key');
        if (translations[currentLang][key]) {
            element.innerHTML = translations[currentLang][key];
        }
    });
    langToggleBtn.textContent = currentLang === 'en' ? 'हिन्दी' : 'English';
};

langToggleBtn.addEventListener('click', () => {
    currentLang = currentLang === 'en' ? 'hi' : 'en';
    updateContent();
});

// --- CSRF Token ---
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// --- Recommendation Logic ---
const fetchRecommendations = (userData) => {
    wizardForm.classList.add('hidden');
    loader.classList.remove('hidden');

    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(userData),
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        loader.classList.add('hidden');
        displayResults(data);
    })
    .catch(error => {
        console.error('Error fetching recommendations:', error);
        loader.classList.add('hidden');
        resultsContainer.innerHTML = `<p>An error occurred. Please try again later.</p>`;
        resultsArea.classList.remove('hidden');
    });
};

// --- Wizard Navigation ---
document.querySelectorAll('[data-next]').forEach(button => {
    button.addEventListener('click', () => {
        const nextStep = button.getAttribute('data-next');
        document.querySelector('.step.active').classList.remove('active');
        document.getElementById(`step-${nextStep}`).classList.add('active');
        updateProgressBar();
    });
});

document.querySelectorAll('[data-prev]').forEach(button => {
    button.addEventListener('click', () => {
        const prevStep = button.getAttribute('data-prev');
        document.querySelector('.step.active').classList.remove('active');
        document.getElementById(`step-${prevStep}`).classList.add('active');
        updateProgressBar();
    });
});

function updateProgressBar() {
    const activeStep = document.querySelector('.step.active');
    const stepNumber = parseInt(activeStep.id.replace('step-', ''), 10);
    const progress = Math.max(0, (stepNumber - 2) / (totalSteps - 1)) * 100;
    progressBar.style.width = `${progress}%`;
}


// --- Tag & Card Selection ---
skillsContainer.addEventListener('click', (e) => {
    if (e.target.classList.contains('tag')) {
        e.target.classList.toggle('selected');
    }
});

interestsContainer.addEventListener('click', (e) => {
    const card = e.target.closest('.interest-card');
    if (card) {
        card.classList.toggle('selected');
    }
});


// --- Event Listeners ---
submitBtn.addEventListener('click', () => {
    const userData = {
        skills: Array.from(skillsContainer.querySelectorAll('.tag.selected')).map(tag => tag.getAttribute('data-skill')),
        interests: Array.from(interestsContainer.querySelectorAll('.interest-card.selected')).map(card => card.getAttribute('data-interest')),
        degree: document.getElementById('degree').value,
        field: document.getElementById('field').value,
        location: document.getElementById('location').value,
        wfhOnly: document.getElementById('wfh-checkbox').checked,
    };
    fetchRecommendations(userData);
});

// --- Display & Modal Logic ---
const displayResults = (results) => {
    resultsContainer.innerHTML = '';
    if (results.length === 0) {
        resultsContainer.innerHTML = `<p>No internships found matching your criteria.</p>`;
    } else {
        results.forEach(internship => {
            const card = document.createElement('div');
            card.classList.add('internship-card');
            card.innerHTML = `
                <h3>${internship.title}</h3>
                <p class="company">${internship.company}</p>
                <div class="match-bar-container">
                    <div class="match-bar" style="width: ${internship.match_percentage}%;"></div>
                    <span>${internship.match_percentage}% Match</span>
                </div>
                <p class="match-reason">${internship.match_reason}</p>
                <div class="tags">
                    <span class="tag">${internship.location}</span>
                    <span class="tag">${internship.duration}</span>
                    <span class="tag">${internship.stipend}</span>
                </div>
            `;
            card.addEventListener('click', () => showModal(internship));
            resultsContainer.appendChild(card);
        });
    }
    resultsArea.classList.remove('hidden');
};

const modal = document.getElementById('details-modal');
const showModal = (internship) => {
    console.log("Internship data for model:", internship);
    document.getElementById('modal-title').textContent = internship.title;
    document.getElementById('modal-company').textContent = internship.company;
    document.getElementById('modal-location').textContent = internship.location;
    document.getElementById('modal-duration').textContent = internship.duration;
    document.getElementById('modal-stipend').textContent = internship.stipend;
    document.getElementById('modal-description').textContent = internship.description;
    document.getElementById('modal-apply-btn').href = internship.apply_link;

    const skillGapSection = document.getElementById('skill-gap-section');
    const missingSkillsContainer = document.getElementById('missing-skills-container');
    missingSkillsContainer.innerHTML = '';

    if (internship.missing_skills && internship.missing_skills.length > 0) {
        internship.missing_skills.forEach(item => {
            const skillElement = document.createElement('div');
            skillElement.classList.add('skill-item');
            
            // Create a simple roadmap dropdown (accordion)
            const roadmapHtml = item.roadmap.map(step => `<li>${step}</li>`).join('');

            skillElement.innerHTML = `
                <div class="skill-header">
                    <strong>${item.skill}</strong>
                    <a href="${item.youtube_link}" target="_blank" class="youtube-btn">Watch Tutorial 📺</a>
                </div>
                <details class="roadmap">
                    <summary>View Learning Roadmap</summary>
                    <ul>${roadmapHtml}</ul>
                </details>
            `;
            missingSkillsContainer.appendChild(skillElement);
        });
        skillGapSection.classList.remove('hidden');
    } else {
        skillGapSection.classList.add('hidden');
    }

    modal.classList.remove('hidden');
};


modal.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay') || e.target.classList.contains('modal-close-btn')) {
        modal.classList.add('hidden');
    }
});

// --- Initial Calls on Page Load ---
updateProgressBar();
updateContent();