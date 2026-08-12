from google_meet import create_meeting_space

if __name__ == '__main__':
    try:
        url = create_meeting_space()
        print('Google Meet test succeeded.')
        print('Meet URL:', url)
    except Exception as exc:
        print('Google Meet test failed:')
        print(type(exc).__name__ + ':', exc)
        raise SystemExit(1)
