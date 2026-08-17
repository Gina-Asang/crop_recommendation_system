const form = document.getElementById('crop-form');
const submitBtn = document.getElementById('submit-btn');
const errorBox = document.getElementById('error-box');

const resultEmpty = document.getElementById('result-empty');
const resultSuccess = document.getElementById('result-success');
const resultStatus = document.getElementById('result-status');

const cropName = document.getElementById('crop-name');
const cropPhoto = document.getElementById('crop-photo');
const cropPhotoWrap = document.querySelector('.crop-photo-wrap');

const explanationTitle = document.getElementById('explanation-title');
const modelExplanation = document.getElementById('model-explanation');
const topPredictions = document.getElementById('top-predictions');

const sampleBtn = document.getElementById('sample-btn');
const resetBtn = document.getElementById('reset-btn');


const fields = [
    'N',
    'P',
    'K',
    'temperature',
    'humidity',
    'ph',
    'rainfall'
];


const sample = {
    N: 90,
    P: 42,
    K: 43,
    temperature: 20.88,
    humidity: 82,
    ph: 6.5,
    rainfall: 202.94
};


/*
Crop images are visual only.
They are not used by the machine-learning model.
*/
const cropImageTerms = {
    apple: 'apple fruit tree farm',
    banana: 'banana plant farm',
    blackgram: 'black gram crop plant',
    chickpea: 'chickpea crop farm',
    coconut: 'coconut palm farm',
    coffee: 'coffee plant farm',
    cotton: 'cotton crop field',
    grapes: 'grape vineyard',
    jute: 'jute crop field',
    kidneybeans: 'kidney bean crop plant',
    lentil: 'lentil crop plant',
    maize: 'maize corn field',
    mango: 'mango tree farm',
    mothbeans: 'moth bean crop',
    mungbean: 'mung bean crop',
    muskmelon: 'muskmelon crop farm',
    orange: 'orange tree farm',
    papaya: 'papaya pawpaw tree farm',
    pigeonpeas: 'pigeon pea crop',
    pomegranate: 'pomegranate tree fruit',
    rice: 'rice paddy field',
    watermelon: 'watermelon crop field'
};



// ERRORS


function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.add('show');
}


function clearError() {
    errorBox.textContent = '';
    errorBox.classList.remove('show');
}



// INPUT VALIDATION


function clearInvalidStates() {
    fields.forEach((key) => {
        const input = document.getElementById(key);

        input
            .closest('.input-shell')
            .classList.remove('invalid');
    });
}


function getFieldName(input) {
    const field = input.closest('.field');

    if (!field) {
        return input.name;
    }

    const fieldName = field.querySelector('.field-name');

    if (!fieldName) {
        return input.name;
    }

    return fieldName.textContent.trim();
}


function validateInputs() {
    clearInvalidStates();

    for (const key of fields) {
        const input = document.getElementById(key);
        const value = input.value.trim();

        if (value === '') {
            input
                .closest('.input-shell')
                .classList.add('invalid');

            input.focus();

            return (
                'Please complete all seven fields before ' +
                'requesting a recommendation.'
            );
        }

        const number = Number(value);
        const minimum = Number(input.min);
        const maximum = Number(input.max);

        if (
            !Number.isFinite(number) ||
            number < minimum ||
            number > maximum
        ) {
            input
                .closest('.input-shell')
                .classList.add('invalid');

            input.focus();

            return (
                `${getFieldName(input)} must be between ` +
                `${minimum} and ${maximum}.`
            );
        }
    }

    return null;
}



// CROP IMAGE


function setCropPhoto(crop) {
    const key = String(crop)
        .toLowerCase()
        .replace(/\s+/g, '');

    const searchTerm =
        cropImageTerms[key] || `${crop} crop farm`;

    const lock = Array.from(key).reduce(
        (total, character) =>
            total + character.charCodeAt(0),
        0
    );

    cropPhotoWrap.classList.remove('has-image');

    cropPhoto.alt = `${crop} crop`;

    cropPhoto.src =
        `https://loremflickr.com/1000/700/` +
        `${encodeURIComponent(searchTerm)}?lock=${lock}`;

    cropPhoto.onload = () => {
        cropPhotoWrap.classList.add('has-image');
    };

    cropPhoto.onerror = () => {
        cropPhotoWrap.classList.remove('has-image');
    };
}



// RESET


function resetResult() {
    resultSuccess.hidden = true;
    resultEmpty.hidden = false;

    resultStatus.textContent = 'Ready';

    cropPhoto.src = '';
    cropPhotoWrap.classList.remove('has-image');

    modelExplanation.innerHTML = '';
    topPredictions.innerHTML = '';

    clearError();
    clearInvalidStates();
}


sampleBtn.addEventListener('click', () => {
    fields.forEach((key) => {
        document.getElementById(key).value = sample[key];
    });

    clearError();
    clearInvalidStates();
});


form.addEventListener('reset', () => {
    setTimeout(resetResult, 0);
});


resetBtn.addEventListener('click', () => {
    form.reset();

    document.getElementById('N').focus();

    document.getElementById('recommend').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
});



// LIVE RANGE CHECKING


fields.forEach((key) => {
    const input = document.getElementById(key);

    input.addEventListener('input', () => {
        const value = Number(input.value);
        const minimum = Number(input.min);
        const maximum = Number(input.max);

        const wrapper = input.closest('.input-shell');

        if (
            input.value !== '' &&
            (
                !Number.isFinite(value) ||
                value < minimum ||
                value > maximum
            )
        ) {
            wrapper.classList.add('invalid');
        } else {
            wrapper.classList.remove('invalid');
        }
    });
});



// SUBMIT


form.addEventListener('submit', async (event) => {
    event.preventDefault();

    clearError();

    const validationError = validateInputs();

    if (validationError) {
        showError(validationError);
        return;
    }

    const payload = {};

    fields.forEach((key) => {
        payload[key] = Number(
            document.getElementById(key).value
        );
    });

    submitBtn.classList.add('loading');
    submitBtn.disabled = true;

    resultStatus.textContent = 'Analyzing...';

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',

            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error ||
                'Prediction could not be completed.'
            );
        }


        
        // RECOMMENDED CROP
   

        cropName.textContent = data.recommended_crop;

        setCropPhoto(data.recommended_crop);


        
        // MODEL EXPLANATION
      

        explanationTitle.textContent =
            `What Influenced the ${data.recommended_crop} Prediction?`;

        modelExplanation.innerHTML = '';

        const explanations = data.model_explanation || [];

        explanations.forEach((item, index) => {
            const row = document.createElement('article');

            row.className = 'explanation-item';

            row.innerHTML = `
                <div class="explanation-top">
                    <span class="explanation-rank">
                        ${index + 1}
                    </span>

                    <div class="explanation-heading">
                        <strong>${item.feature}</strong>
                        <span>${item.rank_label}</span>
                    </div>

                    <span class="explanation-value">
                        ${item.value}
                    </span>
                </div>

                <p>
                    ${item.text}
                </p>

                <div
                    class="contribution-track"
                    aria-hidden="true"
                >
                    <span
                        style="width:
                        ${Math.max(
                            Number(item.relative_strength),
                            8
                        )}%"
                    ></span>
                </div>
            `;

            modelExplanation.appendChild(row);
        });


       
        // TOP THREE MODEL PREDICTIONS
     

        topPredictions.innerHTML = '';

        const predictions = data.top_predictions || [];

        predictions.forEach((item, index) => {
            const row = document.createElement('div');

            row.className = 'top-three-item';

            row.innerHTML = `
                <span class="top-three-number">
                    ${index + 1}
                </span>

                <div class="top-three-main">
                    <span class="top-three-name">
                        ${item.crop}
                    </span>

                    <span class="top-three-label">
                        Model probability
                    </span>
                </div>

                <strong class="top-three-probability">
                    ${item.probability}%
                </strong>
            `;

            topPredictions.appendChild(row);
        });


        resultEmpty.hidden = true;
        resultSuccess.hidden = false;

        resultStatus.textContent = 'Prediction complete';

        if (window.innerWidth < 1260) {
            document
                .getElementById('result-panel')
                .scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
        }

    } catch (error) {
        resultStatus.textContent = 'Ready';

        showError(
            error.message ||
            'Something went wrong. Please try again.'
        );

    } finally {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
    }
});