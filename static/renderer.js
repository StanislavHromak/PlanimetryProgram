/**
 * @typedef {'header'|'rule'|'info'|'step'|'error'} StepType
 *
 * @typedef {Object} Step
 * @property {StepType} type
 * @property {string} [text]
 * @property {string} [title]
 * @property {string} [formula]
 * @property {string} [solution]
 * @property {string} [rule]
 */

export function renderStep(step) {
    switch (step.type) {
        case 'header':
            return `
                <div class="step-card">
                    <div class="step-title">➤ ${step.text}</div>
                </div>`;

        case 'rule':
            return `
                <div class="rule-box">
                    📌 ${step.text}
                </div>`;

        case 'info':
            return `
                <div class="step-description">
                    ${step.text}
                </div>`;

        case 'step':
            return `
                <div class="step-card">
                    <div class="step-title">➤ ${step.title}</div>
                    ${step.rule ? `<div class="rule-box">📌 ${step.rule}</div>` : ''}
                    ${step.formula ? `<div class="formula-box">${step.formula}</div>` : ''}
                    <div class="step-description">
                        ${step.solution} = <span class="step-result">${step.value}</span>
                    </div>
                </div>`;

        case 'intermediate':
            return `
                <div class="step-card step-card--intermediate">
                    <div class="step-title--intermediate">↳ ${step.title}</div>
                    ${step.rule ? `<div class="rule-box">📌 ${step.rule}</div>` : ''}
                    ${step.formula ? `<div class="formula-box formula-box--sm">${step.formula}</div>` : ''}
                    <div class="step-description">
                        ${step.solution} = <span class="step-result">${step.value}</span>
                    </div>
                </div>`;

        default:
            return `<div class="step-description">${JSON.stringify(step)}</div>`;
    }
}