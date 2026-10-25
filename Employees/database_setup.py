'''Setup the Employees Database'''

## Imports 
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Employee(Base):
	__tablename__ = 'employee'
	
	name = Column(String(250), nullable = False)
	id = Column(Integer, primary_key = True)

class Address(Base):
	__tablename__ = 'address'

	street = Column(String(80), nullable = False)
	zip = Column(String(5), nullable = False)
	id = Column(Integer, primary_key = True)
	employee_id = Column(Integer, ForeignKey('employee.id'))
	employee = relationship(Employee)

engine = create_engine('sqlite:///employees.db')
Base.metadata.create_all(engine)