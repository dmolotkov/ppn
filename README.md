# ppn

## Семейный футбол — план на 2 недели

PDF-план домашних тренировок для троих детей (6 / 9 / 11 лет):  
**3 тренировки в неделю × 25–30 минут**, все упражнения идут одной лентой, у каждого упражнения есть визуальная схема.

### Файл

- [`family_football_2weeks.pdf`](./family_football_2weeks.pdf) — готовый план со схемками
- [`generate_training_pdf.py`](./generate_training_pdf.py) — генератор PDF

### Пересобрать PDF

```bash
pip install reportlab
python3 generate_training_pdf.py
```

Нужен шрифт DejaVu Sans (обычно есть в Linux: `/usr/share/fonts/truetype/dejavu/`).
