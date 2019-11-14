
class Documento:
    def __init__(self, titulo):
        self.titulo = titulo
        self.perguntas = []

    def add_pergunta(self, nome, figura):
        self.perguntas.append((nome, figura))

    def texto(self):
        lines = ["<!DOCTYPE html><html><head></head>"]
        for p, img in self.perguntas:
            lines.append("<h2> {} </h2>".format(p))
            lines.append("<p> <img src=\"{}\" /> </p>".format(img))
        lines.append("</html>")
        return "\n".join(lines)