"""
Пример использования конвертера PPTX в PDF
"""
from pptx_to_pdf_converter import PPTXToPDFConverter
import sys

def convert_pptx_to_pdf(pptx_file: str, output_pdf: str = None):
    """
    Конвертирует PPTX файл в PDF с поддержкой видео
    
    Args:
        pptx_file: путь к PPTX файлу
        output_pdf: путь к выходному PDF файлу (опционально)
    """
    if output_pdf is None:
        import os
        base_name = os.path.splitext(pptx_file)[0]
        output_pdf = f"{base_name}.pdf"
    
    print(f"Конвертация: {pptx_file} → {output_pdf}")
    
    with PPTXToPDFConverter(pptx_file, output_pdf) as converter:
        converter.convert()
    
    print(f"\n✓ Конвертация завершена!")
    return output_pdf


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python example_convert.py <путь_к_pptx> [путь_к_pdf]")
        print("\nПример:")
        print("  python example_convert.py presentation.pptx")
        print("  python example_convert.py presentation.pptx output.pdf")
        sys.exit(1)
    
    pptx_file = sys.argv[1]
    output_pdf = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        convert_pptx_to_pdf(pptx_file, output_pdf)
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

