class UndoRedo:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def do(self, undo_fn, redo_fn):
        redo_fn()
        self.undo_stack.append((undo_fn, redo_fn))
        self.redo_stack.clear()

    def undo(self):
        try:
            undo_fn, redo_fn = self.undo_stack.pop()
            undo_fn()
            self.redo_stack.append((undo_fn, redo_fn))
        except IndexError:
            pass

    def redo(self):
        try:
            undo_fn, redo_fn = self.redo_stack.pop()
            redo_fn()
            self.undo_stack.append((undo_fn, redo_fn))
        except IndexError:
            pass
