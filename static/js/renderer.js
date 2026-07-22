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
                    ${step.text}
                </div>`;

        case 'info':
            return `
                <div class="step-description">
                    ${step.text}
                </div>`;

        case 'step': {
            const suffix = step.show_result_suffix === false
                ? ''
                : ` = <span class="step-result">${step.value}</span>`;
            return `
                <div class="step-card">
                    <div class="step-title">➤ ${step.title}</div>
                    ${step.rule ? `<div class="rule-box">${step.rule}</div>` : ''}
                    ${step.formula ? `<div class="formula-box" style="font-size: 1.1em; overflow-x: auto;">$$${step.formula}$$</div>` : ''}
                    <div class="step-description" style="margin-top: 10px; font-size: 1.15em;">
                        \\(${step.solution}\\)${suffix}
                    </div>
                </div>`;
        }

        case 'intermediate': {
            const suffix = step.show_result_suffix === false
                ? ''
                : ` = <span class="step-result">${step.value}</span>`;
            return `
                <div class="step-card step-card--intermediate">
                    <div class="step-title--intermediate">↳ ${step.title}</div>
                    ${step.rule ? `<div class="rule-box">${step.rule}</div>` : ''}
                    ${step.formula ? `<div class="formula-box formula-box--sm" style="overflow-x: auto;">$$${step.formula}$$</div>` : ''}
                    <div class="step-description" style="margin-top: 8px;">
                        \\(${step.solution}\\)${suffix}
                    </div>
                </div>`;
        }

        default:
            return `<div class="step-description">${JSON.stringify(step)}</div>`;
    }
}