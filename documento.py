
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
        lines.append("<h1> {} </h1>".format(self.titulo))
        for p, valor, tipo in self.perguntas:
            lines.append("<h2> {} </h2>".format(p))
            if tipo == 0:
                (img, disc, fase, curso) = valor
                lines.append("<p> Total de respostas da disciplina = {} </p>".format(disc))
                lines.append("<p> Total de respostas da fase = {} </p>".format(fase))
                lines.append("<p> Total de respostas do curso = {} </p>".format(curso))
                lines.append("<p> <img src=\"{}\" /> </p>".format(img))
            else:
                for resp in valor:
                    lines.append("<p> {} </p>".format(resp))
        lines.append("</html>")
        return "\n".join(lines)