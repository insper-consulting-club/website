from .models import Participant


def participe(request):
    """
    Mantida apenas para quando o Mailing for integrado ao React.
    Receberá POST com name, email, course, semester, reason.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        course = request.POST.get('course')
        semester = request.POST.get('semester')
        reason = request.POST.get('reason')

        if all([name, email, course, semester, reason]):
            Participant.objects.create(
                name=name,
                email=email,
                course=course,
                semester=semester,
                reason=reason
            )
