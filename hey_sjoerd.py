from dotenv import load_dotenv
import os
load_dotenv()

# Plaats hier je API key of zet hem in de .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

from typing import Literal
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

# Mockup van de documentinhoud
mockup_inhoud = """Titelblad: VERTROUWELIJK HR-POLICY
Afdeling: HR
Datum: 15-05-2025

Dit document bevat vertrouwelijke richtlijnen en procedures voor het aannemen van nieuw personeel,
inclusief gedragscodes, beoordelingscriteria en salarisinformatie.

De bewaartermijn weten we eigenlijk niet. We gokken op 3 jaar maar het kan ook 4 jaar zijn. Geen idee eigenlijk.

"""

class GevoeligheidLabel(BaseModel):
    redenering: str
    zekerheid: Literal["Zeker", "Twijfel", "Onzeker"]
    categorie: Literal["Vertrouwelijk", "Niet vertrouwelijk"]

class BewaartermijnLabel(BaseModel):
    redenering: str
    zekerheid: Literal["Zeker", "Twijfel", "Onzeker"]
    categorie: str  # model bepaalt zelf

class DoelbindingLabel(BaseModel):
    redenering: str
    zekerheid: Literal["Zeker", "Twijfel", "Onzeker"]
    categorie: Literal["IT", "HR", "Finance", "Marketing", "Overig"]

class DocumentLabels(BaseModel):
    gevoeligheid: GevoeligheidLabel
    bewaartermijn: BewaartermijnLabel
    doelbinding: DoelbindingLabel

rules_gevoeligheid = """– **Gevoeligheid**:
Bij categorie "Vertrouwelijk":
  • Zeker: er staat expliciet "VERTROUWELIJK" op titelblad of in inhoud.
  • Twijfel: geen expliciete vermelding, maar bevat bedrijfsspecifieke data.
  • Onzeker: mogelijk openbaar maar context blijft onduidelijk.

Bij categorie "Niet vertrouwelijk":
  • Zeker: expliciet bestemd voor algemeen gebruik of publicatie.
  • Twijfel: geen vertrouwelijke termen, maar geen expliciete vrijgave.
  • Onzeker: onvoldoende context om uitsluiting te garanderen.
"""

rules_bewaartermijn = """– **Bewaartermijn**:
Bij het bepalen van de bewaartermijn:
  • Zeker: Er staat expliciet een bewaartermijn in het document vermeld (bijv. "Bewaren: 5 jaar").
  • Twijfel: Er is geen expliciete termijn, of deze is onduidelijk vermeld.
  • Onzeker: Er is volledig geen indicatie van een bewaartermijn.
  """


rules_doelbinding = """– **Doelbinding**:
Bij categorie "IT":
  • Zeker: inhoud beschrijft technische architectuur of processen.
  • Twijfel: IT-termen maar deels relevant.
  • Onzeker: technische details ontbreken.

Bij categorie "HR":
  • Zeker: behandelt personeelsbeleid of salarissen.
  • Twijfel: enkele HR-termen, maar niet primair.
  • Onzeker: onvoldoende HR-context.

Bij categorie "Finance":
  • Zeker: financiële cijfers of budgettering.
  • Twijfel: financiële termen sporadisch.
  • Onzeker: weinig financiële inhoud.

Bij categorie "Marketing":
  • Zeker: promotiestrategieën of marktanalyses.
  • Twijfel: marketingtermen incidenteel.
  • Onzeker: geen duidelijke marketingfocus.

Bij categorie "Overig":
  • Zeker: valt niet onder bovenstaande categorieën.
  • Twijfel: kan in meerdere categorieën passen.
  • Onzeker: onduidelijk doel.
"""

completion = client.beta.chat.completions.parse(
    model="gpt-4.1",
    messages=[
        {
            "role": "system",
            "content": (
                "Je bent een document‐classificatie‐assistent. "
                "Voor elk label (Gevoeligheid, Bewaartermijn, Doelbinding) schrijf je eerst de redenering "
                "in `redenering`, kies je in `zekerheid` één van [Zeker, Twijfel, Onzeker], "
                "en selecteer je in `categorie` de vaste opties. Volg het regelschema exact."
            )
        },
        {
            "role": "user",
            "content": (
                f"Document: mockup_document.docx\n\n"
                f"Inhoud van het document:\n{mockup_inhoud}\n\n"
                "Pas de volgende regels toe:\n\n"
                f"{rules_gevoeligheid}\n\n"
                f"{rules_bewaartermijn}\n\n"
                f"{rules_doelbinding}\n\n"
                "Geef de output in JSON conform het Pydantic-model."
            )
        }
    ],
    response_format=DocumentLabels,
)

# Parsed resultaat
labels: DocumentLabels = completion.choices[0].message.parsed
print(labels.model_dump_json(indent=2))