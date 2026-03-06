{{ fullname | escape | underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

   {% set public_methods = methods | reject("equalto", "__init__") | reject("equalto", "__new__") | list %}
   {% if public_methods %}
   .. rubric:: Methods

   .. autosummary::

      {% for item in public_methods %}
      ~{{ name }}.{{ item }}
      {% endfor %}
   {% endif %}

   {% if attributes %}
   .. rubric:: Attributes

   .. autosummary::

      {% for item in attributes %}
      ~{{ name }}.{{ item }}
      {% endfor %}
   {% endif %}
