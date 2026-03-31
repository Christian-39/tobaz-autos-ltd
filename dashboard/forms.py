from django import forms
from products.models import Product, Category


class ProductForm(forms.ModelForm):
    """
    Form for creating and editing products.
    """
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'category_type', 'price', 'quantity',
            'description', 'specifications', 'is_active', 'is_featured',
            'meta_title', 'meta_description'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'specifications': forms.Textarea(attrs={'rows': 4}),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        # We exclude 'slug' because your model's save() method handles it
        fields = ['name', 'icon', 'description', 'is_active']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Engine Parts'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'fas fa-car'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Briefly describe this category'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ProductImageForm(forms.Form):
    """
    Form for adding product images.
    """
    image = forms.ImageField(required=False)
    alt_text = forms.CharField(max_length=200, required=False)
    is_primary = forms.BooleanField(required=False)


ProductImageFormSet = forms.formset_factory(ProductImageForm, extra=3, max_num=10)


class ProductVideoForm(forms.Form):
    """
    Form for adding product videos.
    """
    video = forms.FileField(required=False)
    title = forms.CharField(max_length=200, required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)


ProductVideoFormSet = forms.formset_factory(ProductVideoForm, extra=2, max_num=5)
