// Типы данных для функций и функциональных назначений

// Тип для функции
export interface Function {
    id: number;
    name: string;
    code: string;
    description?: string | null;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

// Базовый тип для создания/обновления функции
export interface FunctionCreateDTO {
    name: string;
    code: string;
    description?: string;
    is_active?: boolean;
}

// Тип для фильтров при получении функций
export interface FunctionFilters {
    skip?: number;
    limit?: number;
    is_active?: boolean;
}

// Тип для функционального назначения
export interface FunctionalAssignment {
    id: number;
    position_id: number;
    function_id: number;
    percentage: number;
    is_primary: boolean;
    created_at: string;
    updated_at: string;
}

// Базовый тип для создания/обновления функционального назначения
export interface FunctionalAssignmentCreateDTO {
    position_id: number;
    function_id: number;
    percentage?: number;
    is_primary?: boolean;
}

// Тип для фильтров при получении функциональных назначений
export interface FunctionalAssignmentFilters {
    skip?: number;
    limit?: number;
    position_id?: number;
    function_id?: number;
    is_primary?: boolean;
} 