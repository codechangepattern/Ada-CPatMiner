class SimilarityMetrics:
    @staticmethod
    def chawathe_similarity(src, dst, mappings):
        max_value = max(len(src.get_descendants()), len(dst.get_descendants()))
        return SimilarityMetrics.number_of_mapped_descendants(src, dst, mappings) / max_value

    @staticmethod
    def overlap_similarity(src, dst, mappings):
        min_value = min(len(src.get_descendants()), len(dst.get_descendants()))
        return SimilarityMetrics.number_of_mapped_descendants(src, dst, mappings) / min_value

    @staticmethod
    def dice_similarity(src, dst, mappings):
        return SimilarityMetrics.dice_coefficient(
            SimilarityMetrics.number_of_mapped_descendants(src, dst, mappings),
            len(src.get_descendants()),
            len(dst.get_descendants())
        )

    @staticmethod
    def jaccard_similarity(src, dst, mappings):
        return SimilarityMetrics.jaccard_index(
            SimilarityMetrics.number_of_mapped_descendants(src, dst, mappings),
            len(src.get_descendants()),
            len(dst.get_descendants())
        )

    @staticmethod
    def dice_coefficient(common_elements_nb, left_elements_nb, right_elements_nb):
        return 2.0 * common_elements_nb / (left_elements_nb + right_elements_nb)

    @staticmethod
    def jaccard_index(common_elements_nb, left_elements_nb, right_elements_nb):
        denominator = (left_elements_nb + right_elements_nb - common_elements_nb)
        return common_elements_nb / denominator

    @staticmethod
    def number_of_mapped_descendants(src, dst, mappings):
        dst_descendants = set(dst.get_descendants())
        mapped_descendants = 0

        for src_descendant in src.get_descendants():
            if mappings.is_src_mapped(src_descendant):
                dst_for_src_descendant = mappings.get_dst_for_src(src_descendant)
                if dst_for_src_descendant in dst_descendants:
                    mapped_descendants += 1

        return mapped_descendants
