# Generator Kartu Programmer

Input manual via form web (tanpa edit data.json), mendukung upload foto.
`create.py` TIDAK diubah; API menjalankannya apa adanya di folder sementara.

## Deploy ke Vercel
1. Upload folder ini ke GitHub, lalu Import di vercel.com (Framework: Other), klik Deploy.
   Atau via CLI: `npm i -g vercel` lalu `vercel --prod` di folder ini.
2. Buka URL yang diberikan Vercel.

## Struktur
- public/index.html  : form input + upload foto
- api/generate.py    : serverless function (menjalankan create.py)
- create.py, font/, src/Template.png : file asli
- data.example.json  : contoh format data lama (tidak dipakai lagi)
