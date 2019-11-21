
class Documento:
    def __init__(self, titulo):
        self.titulo = titulo
        self.perguntas = []

    def add_pergunta(self, nome, figura):
        self.perguntas.append((nome, figura, 0))

    def add_pergunta_textual(self, nome, texto):
        self.perguntas.append((nome, texto, 1))

    def texto(self):
        lines = ["<!DOCTYPE html><html><head></head>"]
        for p, img, tipo in self.perguntas:
            lines.append("<h2> {} </h2>".format(p))
            if tipo == 0:                
                lines.append("<p> <img src=\"{}\" /> </p>".format(img))
            else:
                for resp in img:
                    lines.append("<p> {} </p>".format(resp))
        lines.append("</html>")
        return "\n".join(lines)