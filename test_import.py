try:
    import vertexai
    from vertexai.preview.vision_models import ImageGenerationModel
    print("Successfully imported vertexai and ImageGenerationModel")
except ImportError as e:
    print(f"Failed to import: {e}")
