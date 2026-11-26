"""Launch the upstream MLX server on loopback with an explicit browser origin."""


def restrict_origins(application, middleware_class):
    """Configure upstream CORS before the application builds its middleware stack."""
    cors = [item for item in application.user_middleware if item.cls is middleware_class]
    if len(cors) != 1:
        raise RuntimeError("Expected exactly one upstream CORS middleware")
    cors[0].kwargs["allow_origins"] = ["http://127.0.0.1:8111"]


if __name__ == "__main__":
    from fastapi.middleware.cors import CORSMiddleware
    from mlx_vlm.server.app import app
    from mlx_vlm.server.cli import main

    restrict_origins(app, CORSMiddleware)
    main()
