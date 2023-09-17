
class Progress:
    def __init__(self) -> None:
        self.value = 0
    
    def set(self, progress):
        self.value = progress

# class ProgressManager:
#     def __init__(self) -> None:
#         self.progresses = {}

#     def __call__(self, name: str):
#         if name not in self.progresses:
#             progress = Progress(self)
#             self.progresses[name] = progress
#             return progress
#         else:
#             return self.progresses[name]