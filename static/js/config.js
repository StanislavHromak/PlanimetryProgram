export const uiConfig = {
    regular_polygon: {
        name: "Правильний n-кутник",
        targets: [
            { id: "side", label: "Сторону (a)", checked: false },
            { id: "area", label: "Площу (S)", checked: true },
            { id: "perimeter", label: "Периметр (P)", checked: false },
            { id: "angles", label: "Кути", checked: false },
            { id: "diagonal", label: "Діагональ (d)", checked: false },
            { id: "circumcircle", label: "Описане коло (R)", checked: false },
            { id: "incircle", label: "Вписане коло (r)", checked: false }
        ],
        tasks: {
            "REGULAR_SIDE": {
                name: "Сторона",
                inputs: [ { id: "n", label: "Кількість сторін n" }, { id: "a", label: "Сторона a" } ],
                validTargets: ["area", "perimeter", "angles", "diagonal", "circumcircle", "incircle"]
            },
            "REGULAR_R_CIRCUM": {
                name: "Радіус описаного кола",
                inputs: [ { id: "n", label: "Кількість сторін n" }, { id: "R", label: "Радіус R" } ],
                validTargets: ["side", "area", "perimeter", "angles", "diagonal", "incircle"]
            },
            "REGULAR_R_IN": {
                name: "Радіус вписаного кола",
                inputs: [ { id: "n", label: "Кількість сторін n" }, { id: "r", label: "Радіус r" } ],
                validTargets: ["side", "area", "perimeter", "angles", "diagonal", "circumcircle"]
            },
            "REGULAR_AREA": {
                name: "Площа",
                inputs: [ { id: "n", label: "Кількість сторін n" }, { id: "S", label: "Площа S" } ],
                validTargets: ["side", "perimeter", "angles", "diagonal", "circumcircle", "incircle"]
            },
            "REGULAR_PERIMETER": {
                name: "Периметр",
                inputs: [ { id: "n", label: "Кількість сторін n" }, { id: "P", label: "Периметр P" } ],
                validTargets: ["side", "area", "angles", "diagonal", "circumcircle", "incircle"]
            },
            "REGULAR_ANGLE_SIDE": {
                name: "Внутрішній кут і сторона",
                inputs: [ { id: "alpha", label: "Внутрішній кут α (°)" }, { id: "a", label: "Сторона a" } ],
                validTargets: ["area", "perimeter", "diagonal", "circumcircle", "incircle"]
            }
        }
    },
    triangle: {
        name: "Трикутник",
        hasSubFigures: true,
        subFigures: {
            arbitrary: {
                name: "Довільний трикутник",
                targets: [
                    { id: "angles", label: "Кути (α, β, γ)", checked: false },
                    { id: "side", label: "Невідомі сторони/кути", checked: true },
                    { id: "area", label: "Площу (S)", checked: true },
                    { id: "perimeter", label: "Периметр (P)", checked: false },
                    { id: "incircle", label: "Вписане коло (r)", checked: false },
                    { id: "circumcircle", label: "Описане коло (R)", checked: false }
                ],
                tasks: {
                    "SSS": {
                        name: "Три сторони (SSS)",
                        inputs: [ { id: "a", label: "Сторона a" }, { id: "b", label: "Сторона b" }, { id: "c", label: "Сторона c" } ],
                        validTargets: ["angles", "area", "perimeter", "incircle", "circumcircle"]
                    },
                    "SAS": {
                        name: "Дві сторони і кут між ними (SAS)",
                        inputs: [ { id: "a", label: "Сторона a" }, { id: "b", label: "Сторона b" }, { id: "angle_c", label: "Кут γ (°)" } ],
                        validTargets: ["side", "area", "perimeter", "incircle", "circumcircle"]
                    },
                    "ASA": {
                        name: "Сторона і два прилеглі кути (ASA)",
                        inputs: [ { id: "a", label: "Сторона a" }, { id: "angle_b", label: "Кут β (°)" }, { id: "angle_c", label: "Кут γ (°)" } ],
                        validTargets: ["side", "area", "perimeter", "incircle", "circumcircle"]
                    }
                }
            },
            right: {
                name: "Прямокутний трикутник",
                targets: [
                    { id: "side", label: "Невідому сторону (a)", checked: true },
                    { id: "area", label: "Площу (S)", checked: true },
                    { id: "perimeter", label: "Периметр (P)", checked: false },
                    { id: "incircle", label: "Вписане коло (r)", checked: false },
                    { id: "circumcircle", label: "Описане коло (R)", checked: false }
                ],
                tasks: {
                    "RIGHT_LEGS": {
                        name: "Два катети",
                        inputs: [ { id: "a", label: "Катет a" }, { id: "b", label: "Катет b" } ],
                        validTargets: ["side", "area", "perimeter", "incircle", "circumcircle"]
                    },
                    "RIGHT_LEG_HYPOTENUSE": {
                        name: "Катет і гіпотенуза",
                        inputs: [ { id: "a", label: "Катет a" }, { id: "c", label: "Гіпотенуза c" } ],
                        validTargets: ["side", "area", "perimeter", "incircle", "circumcircle"]
                    }
                }
            },
            isosceles: {
                name: "Рівнобедрений трикутник",
                targets: [
                    { id: "area", label: "Площу (S)", checked: true },
                    { id: "perimeter", label: "Периметр (P)", checked: false },
                    { id: "height", label: "Висоту (h)", checked: false }
                ],
                tasks: {
                    "ISOSCELES_BASE_SIDE": {
                        name: "Основа та бічна сторона",
                        inputs: [ { id: "base", label: "Основа a" }, { id: "side", label: "Бічна сторона b" } ],
                        validTargets: ["area", "perimeter", "height"]
                    }
                }
            },
            equilateral: {
                name: "Рівносторонній трикутник",
                targets: [
                    { id: "area", label: "Площу (S)", checked: true },
                    { id: "perimeter", label: "Периметр (P)", checked: false },
                    { id: "incircle", label: "Вписане коло (r)", checked: false },
                    { id: "circumcircle", label: "Описане коло (R)", checked: false }
                ],
                tasks: {
                    "EQUILATERAL_SIDE": {
                        name: "Сторона",
                        inputs: [ { id: "a", label: "Сторона a" } ],
                        validTargets: ["area", "perimeter", "incircle", "circumcircle"]
                    }
                }
            }
        }
    },
    quadrangle: {
        name: "Чотирикутник",
        hasSubFigures: true,
        subFigures: {
            arbitrary: {
                name: "Довільний чотирикутник",
                targets: [
                    { id: "area", label: "Площу (S)", checked: true },
                    { id: "perimeter", label: "Периметр (P)", checked: false },
                    { id: "circles_check", label: "Вписане/Описане коло?", checked: true }
                ],
                tasks: {
                    "ARB_SIDES_ANGLES": {
                        name: "4 сторони та кут",
                        inputs: [
                            { id: "a", label: "Сторона a (основа)" },
                            { id: "b", label: "Сторона b" },
                            { id: "c", label: "Сторона c" },
                            { id: "d", label: "Сторона d (ліва)" },
                            { id: "angle", label: "Кут α (між a і d) (°)" }
                        ],
                        validTargets: ["area", "perimeter", "circles_check"]
                    }
                }
            },
            parallelogram: {
                name: "Паралелограм",
                targets: [
                    { id: "area",      label: "Площу (S)",             checked: true  },
                    { id: "perimeter", label: "Периметр (P)",           checked: false },
                    { id: "angles",    label: "Кут(и) (α, β)",       checked: false },
                    { id: "diagonals", label: "Діагоналі (d1, d2)",     checked: false },
                    { id: "height",    label: "Висоту (h)",              checked: false },
                    { id: "sides",     label: "Сторони (a, b)",          checked: false }
                ],
                tasks: {
                    "PARALLELOGRAM_S_A": {
                        name: "Дві сторони і кут",
                        inputs: [
                            { id: "a",     label: "Сторона a"  },
                            { id: "b",     label: "Сторона b"  },
                            { id: "angle", label: "Кут α (°)"  }
                        ],
                        validTargets: ["area", "perimeter", "angles", "diagonals", "height"]
                    },
                    "PARALLELOGRAM_D_A": {
                        name: "Діагоналі і кут між ними",
                        inputs: [
                            { id: "d1",    label: "Діагональ d1"       },
                            { id: "d2",    label: "Діагональ d2"       },
                            { id: "angle", label: "Кут між ними γ (°)" }
                        ],
                        validTargets: ["area", "sides", "perimeter", "angles", "height"]
                    }
                }
            },
            rectangle: {
                name: "Прямокутник",
                targets: [
                    { id: "side_b", label: "Другу сторону (b)", checked: true },
                    { id: "area", label: "Площу (S)", checked: true },
                    { id: "perimeter", label: "Периметр (P)", checked: false },
                    { id: "diagonal", label: "Діагональ (d)", checked: false },
                    { id: "circumcircle", label: "Описане коло (R)", checked: false }
                ],
                tasks: {
                    "RECTANGLE_SIDES": {
                        name: "Сторони",
                        inputs: [
                            { id: "a", label: "Сторона a" },
                            { id: "b", label: "Сторона b" }
                        ],
                        validTargets: ["area", "perimeter", "diagonal", "circumcircle"]
                    },
                    "RECTANGLE_AREA_SIDE": {
                        name: "Площа і сторона",
                        inputs: [
                            { id: "a", label: "Відома сторона" },
                            { id: "S", label: "Площа S" }
                        ],
                        validTargets: ["side_b", "perimeter", "diagonal", "circumcircle"]
                    },
                    "RECTANGLE_PERIMETER_SIDE": {
                        name: "Периметр і сторона",
                        inputs: [
                            { id: "a", label: "Відома сторона" },
                            { id: "P", label: "Периметр P" }
                        ],
                        validTargets: ["side_b", "area", "diagonal", "circumcircle"]
                    },
                    "RECTANGLE_DIAGONAL_SIDE": {
                        name: "Діагональ і сторона",
                        inputs: [
                            { id: "a", label: "Відома сторона" },
                            { id: "d", label: "Діагональ d" }
                        ],
                        validTargets: ["side_b", "area", "perimeter", "circumcircle"]
                    }
                }
            },
            rhombus: {
                name: "Ромб",
                targets: [
                    { id: "side_a", label: "Сторону (a)", checked: false },
                    { id: "area", label: "Площу (S)", checked: true },
                    { id: "perimeter", label: "Периметр (P)", checked: false },
                    { id: "height", label: "Висоту (h)", checked: false },
                    { id: "diagonals", label: "Діагоналі (d1, d2)", checked: false },
                    { id: "angles", label: "Кути (α, β)", checked: false },
                    { id: "incircle", label: "Вписане коло (r)", checked: false }
                ],
                tasks: {
                    "RHOMBUS_DIAGONALS": {
                        name: "Діагоналі",
                        inputs: [ { id: "d1", label: "Діагональ d1" }, { id: "d2", label: "Діагональ d2" } ],
                        validTargets: ["side_a", "area", "perimeter", "height", "angles", "incircle"]
                    },
                    "RHOMBUS_SIDE_ANGLE": {
                        name: "Сторона і кут",
                        inputs: [ { id: "a", label: "Сторона a" }, { id: "angle", label: "Кут α (°)" } ],
                        validTargets: ["area", "perimeter", "height", "diagonals", "angles", "incircle"]
                    },
                    "RHOMBUS_AREA_SIDE": {
                        name: "Площа і сторона",
                        inputs: [ { id: "a", label: "Сторона a" }, { id: "S", label: "Площа S" } ],
                        validTargets: ["perimeter", "height", "diagonals", "angles", "incircle"]
                    },
                    "RHOMBUS_DIAGONAL_SIDE": {
                        name: "Діагональ і сторона",
                        inputs: [ { id: "a", label: "Сторона a" }, { id: "d1", label: "Відома діагональ" } ],
                        validTargets: ["area", "perimeter", "height", "diagonals", "angles", "incircle"]
                    }
                }
            },
            square: {
                name: "Квадрат",
                targets: [
                    { id: "side_a", label: "Сторону (a)", checked: false },
                    { id: "area", label: "Площу (S)", checked: true },
                    { id: "perimeter", label: "Периметр (P)", checked: false },
                    { id: "diagonal", label: "Діагональ (d)", checked: false },
                    { id: "incircle", label: "Вписане коло (r)", checked: false },
                    { id: "circumcircle", label: "Описане коло (R)", checked: false }
                ],
                tasks: {
                    "SQUARE_SIDE": {
                        name: "Сторона",
                        inputs: [ { id: "a", label: "Сторона a" } ],
                        validTargets: ["area", "perimeter", "diagonal", "incircle", "circumcircle"]
                    },
                    "SQUARE_AREA": {
                        name: "Площа",
                        inputs: [ { id: "S", label: "Площа S" } ],
                        validTargets: ["side_a", "perimeter", "diagonal", "incircle", "circumcircle"]
                    },
                    "SQUARE_PERIMETER": {
                        name: "Периметр",
                        inputs: [ { id: "P", label: "Периметр P" } ],
                        validTargets: ["side_a", "area", "diagonal", "incircle", "circumcircle"]
                    },
                    "SQUARE_DIAGONAL": {
                        name: "Діагональ",
                        inputs: [ { id: "d", label: "Діагональ d" } ],
                        validTargets: ["side_a", "area", "perimeter", "incircle", "circumcircle"]
                    }
                }
            },
            trapezoid: {
                name: "Трапеція",
                targets: [
                    { id: "midline", label: "Середню лінію (m)", checked: false },
                    { id: "height", label: "Висоту (h)", checked: false },
                    { id: "area", label: "Площу (S)", checked: true },
                    { id: "perimeter", label: "Периметр (P)", checked: false },
                    { id: "angles", label: "Кути (α, β)", checked: false },
                    { id: "diagonals", label: "Діагональ (d)", checked: false },
                    { id: "incircle", label: "Вписане коло (r)", checked: false },
                    { id: "circumcircle", label: "Описане коло (R)", checked: false }
                ],
                tasks: {
                    "TRAPEZOID_ABH": {
                        name: "Основи і висота",
                        inputs: [ { id: "a", label: "Основа a" }, { id: "b", label: "Основа b" }, { id: "h", label: "Висота h" } ],
                        validTargets: ["midline", "area"]
                    },
                    "TRAPEZOID_AREA_BASES": {
                        name: "Площа і основи",
                        inputs: [ { id: "a", label: "Основа a" }, { id: "b", label: "Основа b" }, { id: "S", label: "Площа S" } ],
                        validTargets: ["midline", "height"]
                    },
                    "TRAPEZOID_MIDLINE_HEIGHT": {
                        name: "Середня лінія і висота",
                        inputs: [ { id: "m", label: "Середня лінія m" }, { id: "h", label: "Висота h" } ],
                        validTargets: ["area"]
                    },
                    "ISOSCELES_TRAPEZOID_BASES_LEG": {
                        name: "Рівнобічна: основи і бічна сторона",
                        inputs: [ { id: "a", label: "Основа a" }, { id: "b", label: "Основа b" }, { id: "c", label: "Бічна сторона c" } ],
                        validTargets: ["midline", "height", "area", "perimeter", "angles", "diagonals", "incircle", "circumcircle"]
                    }
                }
            }
        }
    },
    curves: {
        name: "Криволінійні фігури",
        hasSubFigures: true,
        subFigures: {
            circle: {
                name: "Коло та Круг",
                targets: [
                    { id: "radius", label: "Радіус (r)", checked: false },
                    { id: "diameter", label: "Діаметр (d)", checked: false },
                    { id: "area", label: "Площу круга (S)", checked: true },
                    { id: "circumference", label: "Довжину кола (C)", checked: true }
                ],
                tasks: {
                    "CIRCLE_RADIUS": {
                        name: "Радіус",
                        inputs: [ { id: "radius", label: "Радіус r" } ],
                        validTargets: ["diameter", "area", "circumference"]
                    },
                    "CIRCLE_DIAMETER": {
                        name: "Діаметр",
                        inputs: [ { id: "diameter", label: "Діаметр d" } ],
                        validTargets: ["radius", "area", "circumference"]
                    },
                    "CIRCLE_CIRCUMFERENCE": {
                        name: "Довжина кола",
                        inputs: [ { id: "circumference", label: "Довжина C" } ],
                        validTargets: ["radius", "diameter", "area"]
                    },
                    "CIRCLE_AREA": {
                        name: "Площа",
                        inputs: [ { id: "area", label: "Площа S" } ],
                        validTargets: ["radius", "diameter", "circumference"]
                    }
                }
            },
            sector: {
                name: "Сектор та Сегмент",
                targets: [
                    { id: "arc_length", label: "Довжину дуги (L)", checked: true },
                    { id: "sector_area", label: "Площу сектора", checked: true },
                    { id: "perimeter_sector", label: "Периметр сектора", checked: false },
                    { id: "chord_length", label: "Довжину хорди (c)", checked: false },
                    { id: "segment_area", label: "Площу сегмента", checked: false },
                    { id: "segment_height", label: "Висоту сегмента (h)", checked: false }
                ],
                tasks: {
                    "SECTOR_AND_ARC": {
                        name: "Радіус та центральний кут",
                        inputs: [
                            { id: "radius", label: "Радіус r" },
                            { id: "angle", label: "Кут α (°)" }
                        ],
                        validTargets: ["arc_length", "sector_area", "perimeter_sector", "chord_length", "segment_area", "segment_height"]
                    }
                }
            },
            ellipse: {
                name: "Еліпс",
                targets: [
                    { id: "area", label: "Площу (S)", checked: true },
                    { id: "perimeter", label: "Периметр (P)", checked: true },
                    { id: "eccentricity", label: "Ексцентриситет (e)", checked: false }
                ],
                tasks: {
                    "ELLIPSE_AXES": {
                        name: "Пів вісі a та b",
                        inputs: [
                            { id: "a", label: "Велика піввісь a" },
                            { id: "b", label: "Мала піввісь b" }
                        ],
                        validTargets: ["area", "perimeter", "eccentricity"]
                    }
                }
            }
        }
    }
};