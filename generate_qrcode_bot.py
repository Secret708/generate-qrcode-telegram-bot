from aiogram import Bot, Dispatcher
from aiogram.types import Message, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
import os
import qrcode as qr
import time
import asyncio


load_dotenv('tokens/BOTTOKEN.env') # загрузка токена
TOKEN = os.getenv('TOKEN')

if not TOKEN: # проверка на наличие токена
    raise ValueError('not TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()

class qrInfo(StatesGroup): 
    input_text = State()

@dp.message(lambda message: message.text == '/start') # приветственная фраза
async def start(message: Message):
    await message.answer('Привет, я бот для создания QR-кодов. Напиши /gen_qrcode и я начну процесс создания qr-кода')

@dp.message(lambda message: message.text == '/gen_qrcode') # генерация qr-кода
async def data(message: Message, state: FSMContext):
    await state.set_state(qrInfo.input_text)
    await message.answer('Напиши сслыку, слово и тд, чтобы сгенерировать qrcode')
     
@dp.message(qrInfo.input_text) 
async def generate_qrcode(message: Message, state: FSMContext):
    await state.update_data(input_text=message.text)
    data = await state.get_data()
    
    try:
        qrcode = qr.QRCode(
            version=1, 
            error_correction=qr.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
    
        qrcode.add_data(data['input_text'])
        qrcode.make(fit=True)
    
        image = qrcode.make_image(fill_color="black", back_color='white')
        time_generation_qrcode = time.time()
        path_image = f'qr-code_{time_generation_qrcode}.png'
        image.save(path_image)
        send_image = FSInputFile(path_image)

        await message.answer_photo(photo=send_image, caption='Вот ваш QR-код')
        os.remove(path_image)
        await state.clear()
    except Exception as e:
        print(f'Ошибка: {e}')
        await message.answer("Не удалось сгенерировать qr-код")
        await state.clear()
    
async def main(): # главный цикл программы
    while True:
        try:
            print('Start Bot')
            await dp.start_polling(bot, polling_timeout=10)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f'Ошибка: {e}')
            print('Restart Bot')
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())