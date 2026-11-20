import math

class TaskExecutor:
    @staticmethod
    def execute(command, data_str):
        """Передать на сервер множество чисел. Сервер должен вернуть
        сумму этих чисел и наименьший делитель этой суммы (кроме 1 и самой
        суммы). Если делителей нет, вернуть сообщение "сумма простая".
        Пример: {4,6,8} → сумма = 18, наименьший делитель = 2."""

        if command == "TASK6":
            try:
                nums = set()
                for i in data_str.split(","):
                    i = i.strip()
                    if i:
                        nums.add(int(i))

                if not nums:
                    return "[Ошибка]! Пустое множество!"

                ans_sum = sum(nums)

                if ans_sum <= 1:
                    return f"Сумма = {ans_sum}. Делителей нет."

                small_div = None

                end_sum = int(math.isqrt(ans_sum)) + 1

                for i in range(2, end_sum):
                    if ans_sum % i == 0:
                        small_div = i
                        break

                if small_div is not None:
                    return f"Сумма = {ans_sum}. Наименьший делитель = {small_div}."

                else:
                    return f"Сумма = {ans_sum}. Сумма простая"

            except ValueError:
                return "[Ошибка]! Введите числа через запятую (4,6,8)!"
            except Exception as e:
                return f"[Ошибка]! Ошибка при вычислении: {e}"



        return f"[Ошибка]! Неизвестная команда: {command}"