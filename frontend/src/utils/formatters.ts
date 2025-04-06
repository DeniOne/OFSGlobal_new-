/**
 * Набор функций для форматирования данных
 */

/**
 * Форматирует телефонный номер в виде +7 XXX XXX XX XX
 * @param value Исходная строка с телефонным номером
 * @returns Отформатированный телефонный номер
 */
export const maskPhoneNumber = (value: string): string => {
  if (!value) return '';
  
  // Удаляем все нецифровые символы
  const digitsOnly = value.replace(/\D/g, '');
  
  // Форматируем телефон в формате +7 XXX XXX XX XX
  if (digitsOnly.length > 0) {
    let formattedPhone = '';
    
    // Добавляем +7 в начало, если первая цифра 7 или 8, иначе просто +
    if (digitsOnly[0] === '7' || digitsOnly[0] === '8') {
      formattedPhone = '+7 ';
      // Начинаем с индекса 1, пропуская первую цифру
      let i = 1;
      
      // Форматируем остальные цифры
      if (digitsOnly.length > 1) {
        // XXX
        const areaCode = digitsOnly.substring(i, Math.min(i + 3, digitsOnly.length));
        formattedPhone += areaCode;
        i += 3;
        
        // Добавляем пробел после кода города
        if (digitsOnly.length > 4) {
          formattedPhone += ' ';
          
          // XXX
          const part2 = digitsOnly.substring(i, Math.min(i + 3, digitsOnly.length));
          formattedPhone += part2;
          i += 3;
          
          // Добавляем пробел после первых трех цифр номера
          if (digitsOnly.length > 7) {
            formattedPhone += ' ';
            
            // XX
            const part3 = digitsOnly.substring(i, Math.min(i + 2, digitsOnly.length));
            formattedPhone += part3;
            i += 2;
            
            // Добавляем пробел после следующих двух цифр
            if (digitsOnly.length > 9) {
              formattedPhone += ' ';
              
              // XX - последние две цифры
              const part4 = digitsOnly.substring(i, Math.min(i + 2, digitsOnly.length));
              formattedPhone += part4;
            }
          }
        }
      }
    } else {
      // Если номер не начинается с 7 или 8, просто форматируем как есть
      formattedPhone = '+' + digitsOnly;
    }
    
    return formattedPhone;
  }
  
  return value;
}; 