import panzee.nmfe


class MockView(object):

    def __init__(self):
        self.dialogue = ""
        self.speaker = None
        self.background_path = None
        self.background_displaying = False
        self.audio_path = None
        self.audio_playing = False
        self.choices = []
        self.choice = -1
        self.avatars = {}
        self.avatar_pos = {}

    def display_dialogue(self, dialogue):
        self.dialogue = dialogue

    def set_speaker(self, speaker):
        self.speaker = speaker

    def set_background(self, background_path):
        self.background_path = background_path
        self.background_displaying = True

    def clear_background(self):
        self.background_displaying = False

    def play_audio(self, audio_path):
        self.audio_path = audio_path
        self.audio_playing = True

    def stop_audio(self):
        self.audio_path = None
        self.audio_playing = False

    def display_choices(self, choices):
        self.choices = choices

    def set_selected_choice(self, number):
        self.choices = []
        self.choice = number

    def get_selected_choice(self):
        return self.choice

    def set_avatar(self, avatar_name, image_path):
        self.avatars[avatar_name] = image_path

    def get_avatar(self, avatar_name):
        return self.avatars[avatar_name]

    def set_avatar_pos(self, avatar_name, pos):
        self.avatar_pos[avatar_name] = pos

    def exit_avatar(self, avatar_name):
        del self.avatars[avatar_name]
        del self.avatar_pos[avatar_name]

    def restore_context(self, commands):
        for command in commands:
            command.execute()

def auto_step(runtime, num):
    for _ in range(0, num):
        command = runtime.step()
        command.execute()


def test_init():
    view = MockView()
    _ = panzee.nmfe.Runtime(view)


def test_dialogue():
    view = MockView()
    runtime = panzee.nmfe.Runtime(view)
    runtime.read("test/nmfe_test_data/test_dialogue.scn")
    next_command = runtime.step()
    next_command.execute()
    assert view.dialogue == "This is a simple NMF script written to test and and verify the NMF engine."
    # skip some dialogue
    auto_step(runtime, 3)
    assert view.dialogue == "Unlike the previous lines, this will display as a single line."


def test_actor():
    view = MockView()
    runtime = panzee.nmfe.Runtime(view)
    runtime.read("test/nmfe_test_data/test_actors.scn")
    auto_step(runtime, 3)
    assert view.dialogue == "Alright, now we're talking."
    assert view.speaker == "Floyd"
    auto_step(runtime, 2)
    assert view.speaker == None
    assert view.dialogue == "And we're back to narration format."



def test_flags():
    view = MockView()
    runtime = panzee.nmfe.Runtime(view)
    runtime.read("test/nmfe_test_data/test_flags.scn")
    auto_step(runtime, 3)
    assert runtime.get_flag("test_flag") == 1
    assert runtime.get_flag("other_flag") == "bla"
    assert runtime.get_flag("another_flag") == None
    auto_step(runtime, 1)
    assert runtime.has_flag("another_flag") == False


def test_if():
    view = MockView()
    runtime = panzee.nmfe.Runtime(view)
    runtime.read("test/nmfe_test_data/test_if.scn")
    auto_step(runtime, 3)
    assert view.dialogue == "This dialogue will display."
    auto_step(runtime, 3)
    assert view.dialogue == "This dialogue will also display."
    auto_step(runtime, 7)
    assert view.dialogue == "This dialogue will, however."
    auto_step(runtime, 5)
    assert view.dialogue == "This dialogue generated by an else statement will, though."
    auto_step(runtime, 4)
    assert view.dialogue == "This dialog displays."
    auto_step(runtime, 2)
    assert view.dialogue == "This dialog displays."



def test_tree():
    view = MockView()
    runtime = panzee.nmfe.Runtime(view)
    runtime.read("test/nmfe_test_data/test_tree.scn")
    auto_step(runtime, 5)
    assert len(view.choices) == 3
    assert view.choices[0] == "Test choice - spaces joined"
    view.set_selected_choice(3)
    auto_step(runtime, 3)
    assert view.dialogue == "Excellent choice."
    assert runtime.has_flag("choice")
    assert runtime.get_flag("choice") == 3


def test_context():
    view = MockView()
    runtime = panzee.nmfe.Runtime(view)
    runtime.read("test/nmfe_test_data/test_context.scn")
    auto_step(runtime, 2)
    assert view.speaker == "Floyd"
    auto_step(runtime, 2)
    assert view.speaker == "Jermaine"
    runtime.jump_with_context(1)
    # context restoration doesn't execute the index we landed upon, so do that
    auto_step(runtime, 1)
    assert view.speaker == "Floyd"
    assert view.dialogue == "Right now, Floyd is speaking."
    auto_step(runtime, 4)
    assert view.speaker == "Dort"
    assert view.dialogue == "Dort is talking now."
    runtime.jump_with_context(3)
    auto_step(runtime, 1)
    assert view.speaker == "Jermaine"
    assert view.dialogue == "But now, Jermaine is speaking."


def test_scene():
    view = MockView()
    runtime = panzee.nmfe.Runtime(view)
    runtime.read("test/nmfe_test_data/test_scene_pt_1.scn")
    auto_step(runtime, 2)
    assert view.speaker == "Floyd"
    assert view.dialogue == "Let's transition to a scene."
    auto_step(runtime, 3)
    assert view.speaker == "Jermaine"
    assert view.dialogue == "This is Jermaine speaking."
    auto_step(runtime, 2)
    assert view.speaker == "Floyd"
    assert view.dialogue == "This is Floyd speaking again."
