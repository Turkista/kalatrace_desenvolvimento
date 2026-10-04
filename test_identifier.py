from core.identifiers import IdentifierFactory, EntityType

iec = IdentifierFactory.create(EntityType.IEC)
evd = IdentifierFactory.create(EntityType.EVIDENCE)

print(iec)
print(evd)

print(IdentifierFactory.validate(str(iec)))
print(IdentifierFactory.validate(str(evd)))