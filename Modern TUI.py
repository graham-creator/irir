def main():
    try:
        from modern_tui.app import AIClient
        AIClient().run()
    except Exception:
        import traceback
        with open('modern_tui_error.log', 'w') as f:
            f.write(traceback.format_exc())
        raise


if __name__ == '__main__':
    main()
